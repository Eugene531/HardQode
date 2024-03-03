from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.urls import path

from api.views import home, create_course, register, all_courses, course_detail, enroll_course, ProductListAPIView, \
    LessonListAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('create_course/', create_course, name='create_course'),
    path('all_courses/', all_courses, name='all_courses'),
    path('course_detail/<uuid:pk>/', course_detail, name='course_detail'),
    path('enroll_course/<uuid:pk>/', enroll_course, name='enroll_course'),
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('lessons/<uuid:product_id>/', LessonListAPIView.as_view(), name='lesson-list'),
]
