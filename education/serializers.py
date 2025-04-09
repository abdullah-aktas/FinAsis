from rest_framework import serializers
from .models import (
    Course, Lesson, Quiz, QuizQuestion,
    Assignment, StudentSubmission, PerformanceTracking,
    Badge, UserBadge
)

class QuizQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question', 'question_type', 'explanation']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'time_limit', 'passing_score', 'questions']

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'due_date', 'max_score']

class LessonSerializer(serializers.ModelSerializer):
    quizzes = QuizSerializer(many=True, read_only=True)
    assignments = AssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'order', 'video_url', 'duration', 'quizzes', 'assignments']

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'teacher_name', 'level', 'duration', 'thumbnail', 'lessons']

class StudentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSubmission
        fields = ['id', 'assignment', 'submission_file', 'submitted_at', 'score', 'feedback']
        read_only_fields = ['submitted_at', 'score', 'feedback']

class PerformanceTrackingSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = PerformanceTracking
        fields = ['id', 'lesson_title', 'completion', 'quiz_score', 'assignment_score', 'last_accessed']
        read_only_fields = ['last_accessed']

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'icon', 'criteria']

class UserBadgeSerializer(serializers.ModelSerializer):
    badge_details = BadgeSerializer(source='badge', read_only=True)

    class Meta:
        model = UserBadge
        fields = ['id', 'badge_details', 'earned_at']
        read_only_fields = ['earned_at'] 