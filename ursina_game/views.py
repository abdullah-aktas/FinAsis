from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Max, Avg
from .models import Game, GameScore, GameAchievement, UserGameAchievement
from .serializers import (
    GameSerializer, GameScoreSerializer,
    GameAchievementSerializer, UserGameAchievementSerializer
)

# Create your views here.

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        game = self.get_object()
        user_scores = GameScore.objects.filter(game=game, user=request.user)
        all_scores = GameScore.objects.filter(game=game)

        stats = {
            'personal_best': user_scores.aggregate(Max('score'))['score__max'] or 0,
            'average_score': user_scores.aggregate(Avg('score'))['score__avg'] or 0,
            'total_plays': user_scores.count(),
            'global_high_score': all_scores.aggregate(Max('score'))['score__max'] or 0,
            'global_average': all_scores.aggregate(Avg('score'))['score__avg'] or 0,
        }
        return Response(stats)

    @action(detail=True, methods=['get'])
    def leaderboard(self, request, pk=None):
        game = self.get_object()
        top_scores = GameScore.objects.filter(game=game).order_by('-score')[:10]
        serializer = GameScoreSerializer(top_scores, many=True)
        return Response(serializer.data)

class GameScoreViewSet(viewsets.ModelViewSet):
    serializer_class = GameScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GameScore.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        # Başarı kontrolü
        game = serializer.validated_data['game']
        score = serializer.validated_data['score']
        achievements = GameAchievement.objects.filter(game=game)

        for achievement in achievements:
            # Burada başarı kriterlerini kontrol ediyoruz
            # Örnek: Belirli bir skoru geçme
            if 'minimum_score' in achievement.criteria and score >= float(achievement.criteria['minimum_score']):
                UserGameAchievement.objects.get_or_create(
                    user=self.request.user,
                    achievement=achievement
                )

class GameAchievementViewSet(viewsets.ModelViewSet):
    queryset = GameAchievement.objects.all()
    serializer_class = GameAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_achievements(self, request):
        user_achievements = UserGameAchievement.objects.filter(user=request.user)
        serializer = UserGameAchievementSerializer(user_achievements, many=True)
        return Response(serializer.data)

class UserGameAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserGameAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserGameAchievement.objects.filter(user=self.request.user)
