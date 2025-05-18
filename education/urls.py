# -*- coding: utf-8 -*-
from django.urls import path
from . import views

app_name = 'education'

urlpatterns = [
    path('kobi-tutorials/', views.kobi_tutorials, name='kobi_tutorials'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('courses/<int:pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
] 