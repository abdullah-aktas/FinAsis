from django.urls import path
from . import views

app_name = 'blockchain'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/verify/', views.api_verify, name='api_verify'),
    path('records/', views.record_list, name='record_list'),
    path('records/create/', views.record_create, name='record_create'),
] 