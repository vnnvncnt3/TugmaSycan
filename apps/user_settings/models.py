from django.db import models
from django.conf import settings


class UserSettings(models.Model):
    class ExportFormat(models.TextChoices):
        CSV = 'CSV', 'CSV summary'
        PDF = 'PDF', 'PDF breakdown'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    dark_mode = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    default_fair_review = models.BooleanField(default=False)
    export_format = models.CharField(max_length=3, choices=ExportFormat.choices, default=ExportFormat.CSV)

    def __str__(self):
        return f'Settings for {self.user}'