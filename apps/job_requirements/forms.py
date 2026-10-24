from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from apps.skills.utils import get_or_create_skill, normalize_skill_name

from .models import JobRequirement, RequirementCriterion


class RequirementForm(forms.ModelForm):
    class Meta:
        model = JobRequirement
        fields = ['title']
        labels = {'title': 'Requirement title'}
        widgets = {'title': forms.TextInput(attrs={'placeholder': 'e.g. Junior Backend Developer'})}

    def clean_title(self):
        title = ' '.join(self.cleaned_data['title'].split())
        if not title:
            raise forms.ValidationError('Enter a title.')
        return title


class CriterionForm(forms.ModelForm):
    """One criterion row. The skill is typed as text and matched against the Skills
    library (case-insensitive); a new keyword is added to the library on save."""

    skill_name = forms.CharField(
        max_length=50,
        label='Skill or keyword',
        widget=forms.TextInput(attrs={'list': 'skill-options', 'placeholder': 'e.g. Python', 'autocomplete': 'off'}),
    )

    field_order = ['criterion_type', 'skill_name', 'min_years', 'description']

    class Meta:
        model = RequirementCriterion
        fields = ['criterion_type', 'min_years', 'description']
        labels = {'criterion_type': 'Type', 'min_years': 'Minimum years', 'description': 'Note'}
        widgets = {
            'min_years': forms.NumberInput(attrs={'min': 0, 'max': 60, 'placeholder': 'Years'}),
            'description': forms.TextInput(attrs={'placeholder': 'Optional note', 'maxlength': 255}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['criterion_type'].choices = [('', 'Select type')] + list(RequirementCriterion.CriterionType.choices)
        if self.instance.pk and self.instance.skill_id:
            self.fields['skill_name'].initial = self.instance.skill.skill_name

    def clean_skill_name(self):
        name = normalize_skill_name(self.cleaned_data['skill_name'])
        if not name:
            raise forms.ValidationError('Enter a skill or keyword.')
        return name

    def clean(self):
        cleaned = super().clean()
        ctype = cleaned.get('criterion_type')
        years = cleaned.get('min_years')
        if years is not None and ctype and ctype != RequirementCriterion.CriterionType.EXPERIENCE:
            self.add_error('min_years', 'Minimum years only applies to Experience criteria.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.skill, _ = get_or_create_skill(self.cleaned_data['skill_name'])
        if commit:
            instance.save()
        return instance


class BaseCriteriaFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        if 'DELETE' in form.fields:
            # The page's "Remove" button toggles this hidden field instead of a checkbox.
            form.fields['DELETE'].widget = forms.HiddenInput()

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        seen = set()
        active = 0
        for form in self.forms:
            data = getattr(form, 'cleaned_data', None)
            if not data or data.get('DELETE'):
                continue
            active += 1
            key = (data['criterion_type'], data['skill_name'].lower())
            if key in seen:
                label = RequirementCriterion.CriterionType(data['criterion_type']).label
                raise forms.ValidationError(f'"{data["skill_name"]}" is listed twice as {label}. Remove one of them.')
            seen.add(key)
        if active == 0:
            raise forms.ValidationError('Add at least one criterion.')


def build_criteria_formset(extra):
    return inlineformset_factory(
        JobRequirement,
        RequirementCriterion,
        form=CriterionForm,
        formset=BaseCriteriaFormSet,
        extra=extra,
        can_delete=True,
    )
