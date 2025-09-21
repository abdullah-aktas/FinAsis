# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import (
    FinancialTermCard,
    Course, Lesson, LearningOutcome, LessonOutcome, Question, Exam,
    ExamSubmission, ClassSession, AttendanceRecord, PortfolioItem, Tournament, CheatingIncident,
)
from .forms import FinancialTermCardForm
from django.utils.decorators import method_decorator
from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .serializers import (
    CourseSerializer, LessonSerializer, LearningOutcomeSerializer,
    LessonOutcomeSerializer, QuestionSerializer, ExamSerializer,
    ExamSubmissionSerializer, ClassSessionSerializer,
    AttendanceRecordSerializer, PortfolioItemSerializer,
    TournamentSerializer, CheatingIncidentSerializer,
)
from . import services
from .permissions import IsTeacherOfCourseOrReadOnly
 

@login_required
def kobi_tutorials(request):
    return render(request, 'education/kobi_tutorials.html')

@login_required
def index(request):
    return render(request, 'education/index.html')

@login_required
def education_home(request):
    # Ana sayfada gösterilecek özet veriler (sadeleştirilmiş)
    context = {
        'card_count': FinancialTermCard.objects.count(),
        'latest_cards': list(FinancialTermCard.objects.order_by('-id')[:5]),
    }
    return render(request, "education/education_home.html", context)

@method_decorator(login_required, name='dispatch')
class FinancialTermCardListView(ListView):
    model = FinancialTermCard
    template_name = 'education/financialtermcard_list.html'
    context_object_name = 'cards'

@method_decorator(login_required, name='dispatch')
class FinancialTermCardDetailView(DetailView):
    model = FinancialTermCard
    template_name = 'education/financialtermcard_detail.html'
    context_object_name = 'card'

@method_decorator(login_required, name='dispatch')
class FinancialTermCardCreateView(CreateView):
    model = FinancialTermCard
    form_class = FinancialTermCardForm
    template_name = 'education/financialtermcard_form.html'
    success_url = reverse_lazy('education:financialtermcard_list')

@method_decorator(login_required, name='dispatch')
class FinancialTermCardUpdateView(UpdateView):
    model = FinancialTermCard
    form_class = FinancialTermCardForm
    template_name = 'education/financialtermcard_form.html'
    success_url = reverse_lazy('education:financialtermcard_list')

@method_decorator(login_required, name='dispatch')
class FinancialTermCardDeleteView(DeleteView):
    model = FinancialTermCard
    template_name = 'education/financialtermcard_confirm_delete.html'
    success_url = reverse_lazy('education:financialtermcard_list')

# Removed non-LMS API viewsets (analytics, badges, levels, gamification, content, forum, group, feedback)

# ---- LMS viewsets ----
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        # Teachers see their courses; students see enrolled courses
        return Course.objects.filter(Q(teacher=user) | Q(students=user)).distinct()

    def perform_create(self, serializer):
        # Teacher set to the creator
        serializer.save(teacher=self.request.user)

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return Lesson.objects.filter(
            Q(course__teacher=user) | Q(course__students=user)
        ).distinct()

    def perform_create(self, serializer):
        # Ensure creator is teacher of the course
        course = serializer.validated_data.get('course')
        if course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can add lessons.')
        serializer.save()

class LearningOutcomeViewSet(viewsets.ModelViewSet):
    queryset = LearningOutcome.objects.all()
    serializer_class = LearningOutcomeSerializer
    permission_classes = [permissions.IsAuthenticated]

class LessonOutcomeViewSet(viewsets.ModelViewSet):
    serializer_class = LessonOutcomeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return LessonOutcome.objects.filter(
            Q(lesson__course__teacher=user) | Q(lesson__course__students=user)
        ).distinct()

    def perform_create(self, serializer):
        lesson = serializer.validated_data.get('lesson')
        if lesson.course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can map outcomes.')
        serializer.save()

class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['points']
    search_fields = ['text']

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return Question.objects.filter(
            Q(course__teacher=user) | Q(course__students=user)
        ).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can add questions.')
        serializer.save(created_by=self.request.user)

class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return Exam.objects.filter(
            Q(course__teacher=user) | Q(course__students=user)
        ).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can create exams.')
        serializer.save()

class ExamSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        # Students: their own submissions. Teachers: submissions in their courses
        return ExamSubmission.objects.filter(
            Q(student=user) | Q(exam__course__teacher=user)
        ).distinct()

    def perform_create(self, serializer):
        instance = serializer.save(student=self.request.user)
        total, flags = services.grade_submission(instance)
        instance.auto_score = total
        instance.flags = flags
        instance.save(update_fields=["auto_score", "flags"])

    def perform_update(self, serializer):
        instance = serializer.save()
        total, flags = services.grade_submission(instance)
        instance.auto_score = total
        instance.flags = flags
        instance.save(update_fields=["auto_score", "flags"])

class ClassSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return ClassSession.objects.filter(
            Q(course__teacher=user) | Q(course__students=user)
        ).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can create sessions.')
        serializer.save()

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return AttendanceRecord.objects.filter(
            Q(session__course__teacher=user) | Q(student=user)
        ).distinct()

    def perform_create(self, serializer):
        session = serializer.validated_data.get('session')
        if session.course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can record attendance.')
        serializer.save()

class PortfolioItemViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        # Students see their items; teachers see items in their course context
        return PortfolioItem.objects.filter(
            Q(student=user) | Q(course__teacher=user)
        ).distinct()

    def perform_create(self, serializer):
        # Students can create for themselves only
        serializer.save(student=self.request.user)

class TournamentViewSet(viewsets.ModelViewSet):
    serializer_class = TournamentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return Tournament.objects.filter(
            Q(course__teacher=user) | Q(course__students=user) | Q(course__isnull=True)
        ).distinct()

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if course and course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can create tournaments for a course.')
        serializer.save()

class CheatingIncidentViewSet(viewsets.ModelViewSet):
    serializer_class = CheatingIncidentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOfCourseOrReadOnly]

    def get_queryset(self):  # type: ignore[override]
        user = self.request.user
        return CheatingIncident.objects.filter(
            Q(submission__student=user) | Q(submission__exam__course__teacher=user)
        ).distinct()

    def perform_create(self, serializer):
        submission = serializer.validated_data.get('submission')
        if submission.exam.course.teacher_id != self.request.user.pk:
            raise PermissionDenied('Only course teacher can log incidents for submissions in their course.')
        serializer.save()