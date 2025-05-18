# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'blockchain'

urlpatterns = [
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.transaction_create, name='transaction_create'),
    path('transactions/<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/<int:pk>/update/', views.transaction_update, name='transaction_update'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
] 