from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from finance.accounting.models import Voucher, Account
from users.models import User
from .models import Classroom, Assignment, StudentProgress
from .forms import AssignmentGradeForm

def is_teacher(user):
    return user.groups.filter(name='Teachers').exists()

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    """Öğretmen kontrol paneli ana sayfası"""
    context = {
        'classrooms': Classroom.objects.filter(teacher=request.user),
        'recent_assignments': Assignment.objects.filter(teacher=request.user).order_by('-created_at')[:5],
        'student_progress': StudentProgress.objects.filter(
            assignment__teacher=request.user
        ).select_related('student', 'assignment')[:10]
    }
    return render(request, 'education/teacher_dashboard/dashboard.html', context)

class ClassroomListView(ListView):
    """Sınıf listesi görünümü"""
    model = Classroom
    template_name = 'education/teacher_dashboard/classroom_list.html'
    context_object_name = 'classrooms'

    def get_queryset(self):
        return Classroom.objects.filter(teacher=self.request.user)

class ClassroomDetailView(DetailView):
    """Sınıf detay görünümü"""
    model = Classroom
    template_name = 'education/teacher_dashboard/classroom_detail.html'
    context_object_name = 'classroom'

    def get_queryset(self):
        return Classroom.objects.filter(teacher=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignments'] = Assignment.objects.filter(
            classroom=self.object
        ).order_by('-created_at')
        context['students'] = User.objects.filter(
            student_progress__assignment__classroom=self.object
        ).distinct()
        return context

class AssignmentCreateView(CreateView):
    """Ödev oluşturma görünümü"""
    model = Assignment
    template_name = 'education/teacher_dashboard/assignment_form.html'
    fields = ['title', 'description', 'classroom', 'due_date', 'scenario_type']
    success_url = reverse_lazy('teacher_dashboard:assignment_list')

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        messages.success(self.request, 'Ödev başarıyla oluşturuldu.')
        return super().form_valid(form)

class AssignmentDetailView(DetailView):
    """Ödev detay görünümü"""
    model = Assignment
    template_name = 'education/teacher_dashboard/assignment_detail.html'
    context_object_name = 'assignment'

    def get_queryset(self):
        return Assignment.objects.filter(teacher=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_progress'] = StudentProgress.objects.filter(
            assignment=self.object
        ).select_related('student')
        return context

class AssignmentGradeView(UpdateView):
    """Ödev not verme görünümü"""
    model = StudentProgress
    form_class = AssignmentGradeForm
    template_name = 'education/teacher_dashboard/assignment_grade.html'
    success_url = reverse_lazy('teacher_dashboard:assignment_detail')

    def get_object(self):
        assignment = get_object_or_404(
            Assignment,
            pk=self.kwargs['pk'],
            teacher=self.request.user
        )
        return get_object_or_404(
            StudentProgress,
            assignment=assignment,
            student=self.request.user
        )

    def form_valid(self, form):
        messages.success(self.request, 'Not başarıyla kaydedildi.')
        return super().form_valid(form)

class StudentProgressView(DetailView):
    """Öğrenci ilerleme görünümü"""
    model = User
    template_name = 'education/teacher_dashboard/student_progress.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['progress'] = StudentProgress.objects.filter(
            student=self.object,
            assignment__teacher=self.request.user
        ).select_related('assignment')
        return context 