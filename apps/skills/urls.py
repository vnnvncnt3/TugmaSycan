from django.urls import path

from . import views

app_name = 'skills'

urlpatterns = [
    path('', views.skill_list_view, name='list'),
]
