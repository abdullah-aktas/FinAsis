# -*- coding: utf-8 -*-
from django.urls import path
from . import views

urlpatterns = [
    # ... diğer URL'ler ...
    
    # Toplantı URL'leri
    path('meeting/', views.custom_meeting, name='create_meeting'),
    path('meeting/<str:meeting_id>/', views.custom_meeting, name='join_meeting'),
    path('api/meeting/create/', views.create_meeting, name='api_create_meeting'),
    path('api/meeting/<str:meeting_id>/join/', views.join_meeting, name='api_join_meeting'),
    path('api/meeting/<str:meeting_id>/leave/', views.leave_meeting, name='api_leave_meeting'),
    path('api/meeting/<str:meeting_id>/message/', views.send_message, name='api_send_message'),
    path('api/meeting/<str:meeting_id>/whiteboard/', views.update_whiteboard, name='api_update_whiteboard'),
] 