from django.urls import path

from . import views

app_name = 'scoring'

urlpatterns = [
    path('<int:pk>/', views.candidate_detail_view, name='candidate_detail'),
]
