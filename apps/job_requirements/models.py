from django.db import models
from django.conf import settings
from apps.skills.models import Skill

# Create your models here.

class JobRequirement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_requirements'
    )
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class RequirementCriterion(models.Model):
    class CriterionType(models.TextChoices):
        SKILL = 'SK', 'Skill'
        CERTIFICATION = 'CE', 'Certification'
        EXPERIENCE = 'EX', 'Experience'
        LANGUAGE = 'LA', 'Language'

    job_requirement = models.ForeignKey(
        JobRequirement,
        on_delete=models.CASCADE,
        related_name='criteria'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name='requirement_criteria'
    )

    criterion_type = models.CharField(
        max_length=2,
        choices=CriterionType.choices,
    )
    min_years = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.job_requirement} - {self.skill}"
