from django.db import models

# Create your models here.
class Skill(models.Model):
    skill_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.skill_name