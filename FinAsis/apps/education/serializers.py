from rest_framework import serializers
from .models import FinancialTermCard
from .models import StudentAnalytics
from .models import Badge, Level, StudentGamificationProgress
from .models import LearningContent
from .models import Forum, ForumTopic, ForumPost, GroupAssignment
from .models import Feedback

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