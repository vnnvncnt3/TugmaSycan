from django.conf import settings
from django.db import models
from apps.skills.models import Skill


class ResumeBatch(models.Model):
    class Status(models.TextChoices):
        PROCESSING = 'PR', 'Processing'
        COMPLETED = 'CO', 'Completed'
        PARTIALLY_FAILED = 'PF', 'Partially Failed'
        FAILED = 'FA', 'Failed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resume_batches',
    )
    batch_name = models.CharField(max_length=100)
    upload_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.PROCESSING)

    def __str__(self):
        return self.batch_name


class Resume(models.Model):
    class Status(models.TextChoices):
        UPLOADED = 'UP', 'Uploaded'
        REJECTED = 'RJ', 'Rejected'
        FAILED = 'FA', 'Failed'
        PARSED = 'PA', 'Parsed'
        SCORED = 'SC', 'Scored'

    batch = models.ForeignKey(
        ResumeBatch,
        on_delete=models.CASCADE,
        related_name='resumes',
    )
    candidate_name = models.CharField(max_length=100)
    candidate_email = models.CharField(max_length=100)
    file_path = models.CharField(max_length=255)
    raw_text = models.TextField(blank=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.UPLOADED)

    def __str__(self):
        return self.candidate_name


class Education(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='education_entries',
    )
    institution = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.degree} — {self.institution}'


class Certification(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='certifications',
    )
    certificate_name = models.CharField(max_length=100)
    certificate_issuer = models.CharField(max_length=100, blank=True)
    date_obtained = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.certificate_name


class Experience(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='experience_entries',
    )
    company = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.title} at {self.company}'


class ResumeSkill(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='resume_skills',
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name='resume_skills',
    )

    class Meta:
        unique_together = ('resume', 'skill')

    def __str__(self):
        return f'{self.resume} — {self.skill}'