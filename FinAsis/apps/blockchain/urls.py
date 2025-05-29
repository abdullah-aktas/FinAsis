from django.urls import path
from . import views

app_name = 'blockchain'

urlpatterns = [
    path('', views.home, name='home'),
] 