# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'checks'

urlpatterns = [
    path('', views.check_list, name='check_list'),
    path('<int:pk>/', views.check_detail, name='check_detail'),
] 