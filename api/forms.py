from django import forms
from django.contrib.auth.models import User
from api.models import Product, Group, EnrollmentRequest
from django.forms import inlineformset_factory


GroupFormSet = inlineformset_factory(
    Product, Group, fields=['min_users', 'max_users'], extra=1, can_delete=False
)


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'start_date', 'cost', 'num_groups']


class GroupCreationForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'min_users', 'max_users']


class EnrollmentRequestForm(forms.ModelForm):
    class Meta:
        model = EnrollmentRequest
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        course = cleaned_data.get('course')

        # Проверка, что пользователь еще не подавал заявку на этот курс
        if EnrollmentRequest.objects.filter(user=user, course=course, accepted=False).exists():
            raise forms.ValidationError('Вы уже подали заявку на участие в этом курсе.')
