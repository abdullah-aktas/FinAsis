# -*- coding: utf-8 -*-
from rest_framework import serializers
from .models import UrsinaGame, GameScore, GameAchievement, UserGameAchievement, UrsinaPlayer, PlayerWallet, UrsinaGameSession, Tournament, Achievement, PlayerAchievement

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrsinaGame
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

class UrsinaPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrsinaPlayer
        fields = '__all__'

class PlayerWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerWallet
        fields = '__all__'

class UrsinaGameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrsinaGameSession
        fields = '__all__'

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = '__all__'

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'

class PlayerAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerAchievement
        fields = '__all__' 