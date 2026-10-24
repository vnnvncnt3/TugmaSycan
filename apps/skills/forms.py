from django import forms

from .models import Skill
from .utils import normalize_skill_name


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['skill_name']
        labels = {'skill_name': 'Skill or keyword'}
        widgets = {
            'skill_name': forms.TextInput(attrs={
                'placeholder': 'e.g. Python, AWS Cloud Practitioner, Filipino',
                'autocomplete': 'off',
            }),
        }

    def clean_skill_name(self):
        name = normalize_skill_name(self.cleaned_data['skill_name'])
        if not name:
            raise forms.ValidationError('Enter a skill name.')
        existing = Skill.objects.filter(skill_name__iexact=name).first()
        if existing:
            raise forms.ValidationError(f'"{existing.skill_name}" is already in the library.')
        return name
