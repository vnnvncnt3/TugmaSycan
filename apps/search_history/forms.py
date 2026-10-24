from django import forms

from apps.job_requirements.models import JobRequirement
from apps.resumes.models import ResumeBatch


class RunScreeningForm(forms.Form):
    requirement = forms.ModelChoiceField(
        queryset=JobRequirement.objects.none(),
        label='Job requirement',
        empty_label='Select a requirement',
        error_messages={'required': 'Choose a job requirement.'},
    )
    # The batch checkboxes are drawn by hand in the template (they show counts).
    batches = forms.ModelMultipleChoiceField(
        queryset=ResumeBatch.objects.none(),
        error_messages={'required': 'Select at least one resume batch.'},
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['requirement'].queryset = JobRequirement.objects.filter(user=user).order_by('title')
        self.fields['batches'].queryset = ResumeBatch.objects.filter(user=user)
