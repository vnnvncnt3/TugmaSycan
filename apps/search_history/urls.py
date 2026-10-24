from django.urls import path
from . import views

app_name = 'search_history'

urlpatterns = [
    path('history/', views.history_view, name='history'),
]