from django.urls import path
from . import views

app_name = 'resumes'

urlpatterns = [
    path('', views.batch_list_view, name='batch_list'),
    path('upload/', views.upload_view, name='upload'),
    path('batches/<int:pk>/', views.batch_detail_view, name='batch_detail'),
    path('batches/<int:pk>/delete/', views.batch_delete_view, name='batch_delete'),
    path('<int:pk>/', views.resume_detail_view, name='resume_detail'),
]
