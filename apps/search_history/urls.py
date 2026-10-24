from django.urls import path
from . import views

app_name = 'search_history'

urlpatterns = [
    path('', views.history_view, name='history'),
    path('run/', views.run_view, name='run'),
    path('<int:pk>/', views.detail_view, name='detail'),
    path('<int:pk>/delete/', views.delete_view, name='delete'),
]
