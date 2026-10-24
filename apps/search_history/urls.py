from django.urls import path
from . import views

app_name = 'search_history'

urlpatterns = [
    path('', views.history_view, name='history'),
]
