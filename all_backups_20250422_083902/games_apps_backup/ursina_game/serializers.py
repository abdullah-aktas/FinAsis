from rest_framework import serializers
from .models import Game, GameScore, GameAchievement, UserGameAchievement

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'title', 'description', 'game_type', 'scene_file', 'max_score', 'difficulty']

class GameScoreSerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source='game.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = GameScore
        fields = ['id', 'game_title', 'username', 'score', 'completion_percentage', 'played_at', 'duration']
        read_only_fields = ['played_at']

class GameAchievementSerializer(serializers.ModelSerializer):
    game_title = serializers.CharField(source='game.title', read_only=True)

    class Meta:
        model = GameAchievement
        fields = ['id', 'game_title', 'title', 'description', 'criteria', 'points']

class UserGameAchievementSerializer(serializers.ModelSerializer):
    achievement_details = GameAchievementSerializer(source='achievement', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserGameAchievement
        fields = ['id', 'username', 'achievement_details', 'earned_at']
        read_only_fields = ['earned_at'] 