from django.urls import path

from . import views

app_name = 'job_requirements'

urlpatterns = [
    path('', views.requirement_list_view, name='list'),
    path('new/', views.new_requirement_view, name='new_requirement'),
    path('<int:pk>/', views.requirement_detail_view, name='detail'),
    path('<int:pk>/edit/', views.edit_requirement_view, name='edit'),
    path('<int:pk>/delete/', views.requirement_delete_view, name='delete'),
]
