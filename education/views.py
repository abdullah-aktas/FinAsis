from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    Course, Lesson, Quiz, QuizQuestion,
    Assignment, StudentSubmission, PerformanceTracking,
    Badge, UserBadge
)
from .serializers import (
    CourseSerializer, LessonSerializer, QuizSerializer,
    QuizQuestionSerializer, AssignmentSerializer, StudentSubmissionSerializer,
    PerformanceTrackingSerializer, BadgeSerializer, UserBadgeSerializer
)
from django.contrib.auth.decorators import login_required

class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == 'teacher'

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=['get'])
    def student_progress(self, request, pk=None):
        course = self.get_object()
        lessons = course.lessons.all()
        progress_data = []
        
        for lesson in lessons:
            try:
                tracking = PerformanceTracking.objects.get(user=request.user, lesson=lesson)
                progress_data.append({
                    'lesson_id': lesson.id,
                    'lesson_title': lesson.title,
                    'completion': tracking.completion,
                    'quiz_score': tracking.quiz_score,
                    'assignment_score': tracking.assignment_score
                })
            except PerformanceTracking.DoesNotExist:
                progress_data.append({
                    'lesson_id': lesson.id,
                    'lesson_title': lesson.title,
                    'completion': False,
                    'quiz_score': 0,
                    'assignment_score': 0
                })
        
        return Response(progress_data)

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        lesson = self.get_object()
        tracking, created = PerformanceTracking.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        tracking.completion = True
        tracking.save()
        return Response({'status': 'lesson marked as complete'})

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        quiz = self.get_object()
        answers = request.data.get('answers', [])
        correct_count = 0
        total_questions = quiz.questions.count()

        for answer in answers:
            question = get_object_or_404(QuizQuestion, id=answer['question_id'])
            if question.correct_answer == answer['answer']:
                correct_count += 1

        score = (correct_count / total_questions) * 100
        tracking, created = PerformanceTracking.objects.get_or_create(
            user=request.user,
            lesson=quiz.lesson
        )
        tracking.quiz_score = score
        tracking.save()

        return Response({
            'score': score,
            'correct_answers': correct_count,
            'total_questions': total_questions
        })

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

class StudentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'teacher':
            return StudentSubmission.objects.all()
        return StudentSubmission.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class BadgeViewSet(viewsets.ModelViewSet):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]

class UserBadgeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserBadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserBadge.objects.filter(user=self.request.user)

@login_required
def education_home(request):
    return render(request, 'education/home.html')

@login_required
def course_list(request):
    return render(request, 'education/course_list.html')

@login_required
def course_detail(request, course_id):
    return render(request, 'education/course_detail.html', {'course_id': course_id})

@login_required
def lesson_detail(request, lesson_id):
    return render(request, 'education/lesson_detail.html', {'lesson_id': lesson_id})
