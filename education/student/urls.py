# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('assignments/', views.AssignmentListView.as_view(), name='assignment_list'),
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('assignments/<int:pk>/submit/', views.submit_assignment, name='submit_assignment'),
    path('progress/', views.CourseProgressView.as_view(), name='course_progress'),
] 