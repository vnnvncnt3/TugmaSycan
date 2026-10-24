from django import forms
from .models import UserSettings


class SettingsForm(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = ['dark_mode', 'email_notifications', 'default_fair_review', 'export_format']