# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'teacher_dashboard'

urlpatterns = [
    path('', views.teacher_dashboard, name='dashboard'),
    path('classrooms/', views.ClassroomListView.as_view(), name='classroom_list'),
    path('classrooms/<int:pk>/', views.ClassroomDetailView.as_view(), name='classroom_detail'),
    path('assignments/create/', views.AssignmentCreateView.as_view(), name='assignment_create'),
    path('assignments/<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('students/<int:pk>/progress/', views.StudentProgressView.as_view(), name='student_progress'),
    path('assignments/<int:pk>/grade/', views.AssignmentGradeView.as_view(), name='assignment_grade'),
] 