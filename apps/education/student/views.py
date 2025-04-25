from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib import messages
from .models import StudentProfile, StudentAssignment, StudentProgress
from teacher_dashboard.models import Assignment
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponseRedirect

@login_required
def student_dashboard(request):
    """Öğrenci kontrol paneli ana sayfası"""
    student_profile = get_object_or_404(StudentProfile, user=request.user)
    active_assignments = StudentAssignment.objects.filter(
        student=request.user,
        status__in=['not_started', 'in_progress']
    ).select_related('assignment')
    
    recent_grades = StudentAssignment.objects.filter(
        student=request.user,
        status='graded'
    ).select_related('assignment').order_by('-submission_date')[:5]
    
    course_progress = StudentProgress.objects.filter(
        student=request.user,
        status='active'
    ).select_related('course')
    
    context = {
        'profile': student_profile,
        'active_assignments': active_assignments,
        'recent_grades': recent_grades,
        'course_progress': course_progress
    }
    return render(request, 'education/student/dashboard.html', context)

class AssignmentListView(ListView):
    """Ödev listesi görünümü"""
    model = StudentAssignment
    template_name = 'education/student/assignment_list.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        return StudentAssignment.objects.filter(
            student=self.request.user
        ).select_related('assignment').order_by('-assignment__due_date')

class AssignmentDetailView(DetailView):
    """Ödev detay görünümü"""
    model = StudentAssignment
    template_name = 'education/student/assignment_detail.html'
    context_object_name = 'student_assignment'

    def get_queryset(self):
        return StudentAssignment.objects.filter(
            student=self.request.user
        ).select_related('assignment')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = self.object.assignment
        return context

class CourseProgressView(ListView):
    """Ders ilerleme görünümü"""
    model = StudentProgress
    template_name = 'education/student/course_progress.html'
    context_object_name = 'progress_records'

    def get_queryset(self):
        return StudentProgress.objects.filter(
            student=self.request.user
        ).select_related('course').order_by('course__name')

@login_required
def submit_assignment(request, pk):
    """Ödev teslim etme görünümü"""
    student_assignment = get_object_or_404(
        StudentAssignment,
        pk=pk,
        student=request.user
    )
    
    if request.method == 'POST':
        # Ödev dosyasını kaydet
        # İlerleme durumunu güncelle
        student_assignment.status = 'submitted'
        student_assignment.submission_date = timezone.now()
        student_assignment.save()
        
        messages.success(request, 'Ödev başarıyla teslim edildi.')
        return redirect('student:assignment_detail', pk=pk)
    
    return render(request, 'education/student/submit_assignment.html', {
        'student_assignment': student_assignment
    }) 