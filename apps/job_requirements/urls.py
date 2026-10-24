from django.urls import path
from . import views

app_name = 'job_requirements'

urlpatterns = [
    path('new/', views.new_requirement_view, name='new_requirement'),
]