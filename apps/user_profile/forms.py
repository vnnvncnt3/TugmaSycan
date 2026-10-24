from django import forms
from apps.users.models import User
from .models import Profile


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'role', 'organization']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['department']