from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.users.models import User


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'email', 'birth_date', 'role', 'organization']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }