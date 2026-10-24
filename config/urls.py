"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('apps.login.urls')),
    path('register/', include('apps.register.urls')),
    path('profile/', include('apps.user_profile.urls')),
    path('settings/', include('apps.user_settings.urls')),
    path('about/', include('apps.about.urls')),
    path('contact/', include('apps.contact.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('resumes/', include('apps.resumes.urls')),
    path('requirements/', include('apps.job_requirements.urls')),
    path('skills/', include('apps.skills.urls')),
    path('history/', include('apps.search_history.urls')),
    path('', include('apps.home.urls')),
]
