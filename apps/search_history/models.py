from django.db import models
from django.conf import settings
from apps.job_requirements.models import JobRequirement

# Create your models here.

class SearchHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history',
    )
    job_requirement = models.ForeignKey(
        JobRequirement,
        on_delete=models.PROTECT,
        related_name='search_history',
    )
    searched_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f'{self.job_requirement} search on {self.searched_at:%Y-%m-%d}'
 