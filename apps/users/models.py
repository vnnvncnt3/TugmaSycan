from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        HR_MANAGER = 'HR', 'HR Manager'
        RECRUITER = 'RC', 'Recruiter'
        STUDENT_ORG_LEADER = 'SO', 'Student Org Leader'
        PROJECT_MANAGER = 'PM', 'Project Manager'
        OTHER = 'OT', 'Other'

    username = None
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    role = models.CharField(max_length=2, choices=Role.choices, default=Role.OTHER)
    organization = models.CharField(max_length=150, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email