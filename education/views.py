# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Course, Lesson

@login_required
def kobi_tutorials(request):
    return render(request, 'education/kobi_tutorials.html')

@method_decorator(login_required, name='dispatch')
class CourseListView(ListView):
    model = Course
    template_name = 'education/course_list.html'
    context_object_name = 'courses'
    queryset = Course.objects.filter(is_active=True)

@method_decorator(login_required, name='dispatch')
class CourseDetailView(DetailView):
    model = Course
    template_name = 'education/course_detail.html'
    context_object_name = 'course'

@method_decorator(login_required, name='dispatch')
class CourseCreateView(CreateView):
    model = Course
    fields = ['title', 'description', 'category', 'level', 'duration', 'image', 'is_active']
    template_name = 'education/course_form.html'
    success_url = reverse_lazy('education:course_list')

@method_decorator(login_required, name='dispatch')
class CourseUpdateView(UpdateView):
    model = Course
    fields = ['title', 'description', 'category', 'level', 'duration', 'image', 'is_active']
    template_name = 'education/course_form.html'
    success_url = reverse_lazy('education:course_list')

@method_decorator(login_required, name='dispatch')
class CourseDeleteView(DeleteView):
    model = Course
    template_name = 'education/course_confirm_delete.html'
    success_url = reverse_lazy('education:course_list')

@method_decorator(login_required, name='dispatch')
class LessonDetailView(DetailView):
    model = Lesson
    template_name = 'education/lesson_detail.html'
    context_object_name = 'lesson' 