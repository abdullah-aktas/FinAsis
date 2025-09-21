from rest_framework import serializers
from .models import FinancialTermCard
from .models import StudentAnalytics
from .models import Badge, Level, StudentGamificationProgress
from .models import LearningContent
from .models import Forum, ForumTopic, ForumPost, GroupAssignment
from .models import Feedback
from .models import Course, Lesson, LearningOutcome, LessonOutcome, Question, Exam, ExamSubmission, ClassSession, AttendanceRecord, PortfolioItem, Tournament, CheatingIncident

class StudentAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnalytics
        fields = '__all__'

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'

class StudentGamificationProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGamificationProgress
        fields = '__all__'

class LearningContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningContent
        fields = '__all__'

class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = '__all__'

class ForumTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumTopic
        fields = '__all__'

class ForumPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumPost
        fields = '__all__'

class GroupAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupAssignment
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__' 


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        extra_kwargs = {
            'teacher': {'read_only': True},
        }


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class LearningOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningOutcome
        fields = '__all__'


class LessonOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonOutcome
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
        extra_kwargs = {
            'created_by': {'read_only': True},
        }


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'


class ExamSubmissionSerializer(serializers.ModelSerializer):
    total_score = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ExamSubmission
        fields = '__all__'
        extra_kwargs = {
            'student': {'read_only': True},
            'auto_score': {'read_only': True},
            'flags': {'read_only': True},
        }


class ClassSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSession
        fields = '__all__'


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'


class PortfolioItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioItem
        fields = '__all__'
        extra_kwargs = {
            'student': {'read_only': True},
        }


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = '__all__'


class CheatingIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheatingIncident
        fields = '__all__'