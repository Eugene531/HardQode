from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.messages import success
from django.core.checks import messages
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from rest_framework import generics

from api.forms import ProductForm, GroupFormSet, EnrollmentRequestForm
from api.models import Product, Group, UserProfile, EnrollmentRequest, UserProductAccess, Lesson
from api.serializers import ProductSerializer, LessonSerializer


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.annotate(enrolled_users_count=Count('user_access'))

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        print(response.data)  # Печатаем данные перед отправкой ответа
        return response


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        product_id = self.kwargs['product_id']

        # Получаем объект Product или возвращаем 404, если не найден
        product = get_object_or_404(Product, id=product_id)

        # Получаем доступные для пользователя уроки по продукту
        queryset = Lesson.objects.filter(
            product=product, product__user_access__user=user)
        return queryset


@login_required
def all_courses(request):
    courses = Product.objects.all()
    return render(request, 'all_courses.html', {'courses': courses})


@login_required
def home(request):
    user = request.user
    created_courses = Product.objects.filter(creator=user)
    all_courses = Product.objects.all()
    paginator = Paginator(all_courses, 10)
    page = request.GET.get('page')
    courses_page = paginator.get_page(page)
    # Получаем курсы, на которые записался пользователь
    user_enrolled_courses = UserProductAccess.objects.filter(
        user=request.user
    ).values_list('product_id', flat=True)

    return render(request, 'home.html', {'created_courses': created_courses,
                                         'courses_page': courses_page,
                                         'user_enrolled_courses': user_enrolled_courses
                                         }
                  )


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Product, pk=pk)
    groups = Group.objects.filter(product=course)

    # Получаем имя пользователя-автора
    author = "Unknown"
    if course.creator and hasattr(course, 'creator'):
        author = course.creator

    return render(
        request,
        'course_detail.html',
        {'course': course, 'groups': groups, 'author': author}
    )


@login_required
def create_course(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = GroupFormSet(request.POST, prefix='group_formset')

        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)

            # Получаем или создаем профиль пользователя
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)

            # Присваиваем профиль пользователя как создателя продукта
            product.creator = user_profile.user
            product.save()

            groups_info = []
            for group_form in formset:
                if group_form.cleaned_data:
                    min_users = group_form.cleaned_data['min_users']
                    max_users = group_form.cleaned_data['max_users']
                    group = Group.objects.create(
                        product=product, min_users=min_users, max_users=max_users
                    )
                    groups_info.append((group.id, min_users, max_users))

            # Распределение пользователей по группам
            if groups_info:
                pairs = [(request.user.id, info[1], info[2]) for info in groups_info]
                Product.distribute_users_to_groups(pairs, product.num_groups)

            return redirect('home')
    else:
        form = ProductForm()
        formset = GroupFormSet(prefix='group_formset')

    return render(request, 'create_course.html', {'form': form, 'formset': formset})


@login_required
def enroll_course(request, pk):
    course = get_object_or_404(Product, pk=pk)

    # Проверка, является ли пользователь уже участником курса
    if EnrollmentRequest.objects.filter(
            user=request.user, course=course, accepted=True
    ).exists():
        messages.warning(request, 'Вы уже являетесь участником этого курса.')
        return redirect('all_courses')

    if request.method == 'POST':
        form = EnrollmentRequestForm(request.POST)

        if form.is_valid():
            enrollment_request = form.save(commit=False)
            enrollment_request.user = request.user
            enrollment_request.course = course
            enrollment_request.save()

            success(request, 'Ваша заявка на участие в курсе успешно подана.')

            # Обновляем enrolled_users_count у объекта Product
            course.refresh_from_db()

            # Добавим отладочное сообщение
            print(f"Пользователь {request.user.username} успешно записан"
                  f" на курс {course.product_name}")

            return redirect('all_courses')
    else:
        form = EnrollmentRequestForm()

    return render(request, 'enroll_course.html', {'course': course, 'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
