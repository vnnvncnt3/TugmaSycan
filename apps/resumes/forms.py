import os

from django import forms

ALLOWED_EXTENSIONS = ('.pdf', '.docx')
MAX_FILE_MB = 5
MAX_FILES = 100  # matches Django's default DATA_UPLOAD_MAX_NUMBER_FILES


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Standard Django pattern for <input type="file" multiple>."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]
        return [single_file_clean(data, initial)]


class UploadBatchForm(forms.Form):
    batch_name = forms.CharField(
        max_length=100,
        label='Batch name',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Marketing Intern Applicants'}),
    )
    files = MultipleFileField(
        label='Resume files',
        widget=MultipleFileInput(attrs={'accept': ','.join(ALLOWED_EXTENSIONS)}),
    )

    def clean_files(self):
        files = self.cleaned_data['files']
        if not files:
            raise forms.ValidationError('Choose at least one resume file.')
        if len(files) > MAX_FILES:
            raise forms.ValidationError(f'Upload at most {MAX_FILES} files per batch.')
        problems = []
        for f in files:
            ext = os.path.splitext(f.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                problems.append(f'{f.name}: only PDF and DOCX files are supported.')
            elif f.size > MAX_FILE_MB * 1024 * 1024:
                problems.append(f'{f.name}: larger than {MAX_FILE_MB} MB.')
        if problems:
            raise forms.ValidationError(problems)
        return files
