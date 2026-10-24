from django.db import models
from apps.job_requirements.models import JobRequirement, RequirementCriterion
from apps.resumes.models import Resume
from apps.search_history.models import SearchHistory

# Create your models here.
class CandidateScore(models.Model):
    resume = models.ForeignKey(
        Resume,
        on_delete=models.CASCADE,
        related_name='candidate_scores'
    )
    job_requirement = models.ForeignKey(
        JobRequirement,
        on_delete=models.PROTECT,
        related_name='candidate_scores'
    )
    search_history = models.ForeignKey(
        SearchHistory,
        on_delete=models.CASCADE,
        related_name='candidate_scores'
    )
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    scored_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resume} vs {self.job_requirement}: {self.total_score}"

class MatchBreakdown(models.Model):
    class Status(models.TextChoices):
        MET = 'ME', 'Met'
        PARTIAL = 'PA', 'Partial'
        MISSING = 'MI', 'Missing'

    candidate_score = models.ForeignKey(
        CandidateScore,
        on_delete=models.CASCADE,
        related_name='breakdown_items'
    )
    criterion = models.ForeignKey(
        RequirementCriterion,
        on_delete=models.PROTECT,
        related_name='breakdown_items'
    )
    status = models.CharField(max_length=2, choices=Status.choices)

    def __str__(self):
        return f"{self.criterion} - {self.get_status_display()}"
