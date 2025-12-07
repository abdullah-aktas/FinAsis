# -*- coding: utf-8 -*-
from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Max, Avg
from .models import (
    UrsinaGame,
    GameScore,
    GameAchievement,
    UserGameAchievement,
    UrsinaPlayer,
    PlayerWallet,
    UrsinaGameSession,
    Tournament,
    Achievement,
    PlayerAchievement,
)
from .serializers import (
    GameSerializer,
    GameScoreSerializer,
    GameAchievementSerializer,
    UserGameAchievementSerializer,
    UrsinaPlayerSerializer,
    PlayerWalletSerializer,
    UrsinaGameSessionSerializer,
    TournamentSerializer,
    AchievementSerializer,
    PlayerAchievementSerializer,
)
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .controller import FinancialTradingGame

# Create your views here.


class GameViewSet(viewsets.ModelViewSet):
    queryset = UrsinaGame.objects.all()
    serializer_class = GameSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        game = self.get_object()
        user_scores = GameScore.objects.filter(game=game, user=request.user)
        all_scores = GameScore.objects.filter(game=game)

        stats = {
            "personal_best": user_scores.aggregate(Max("score"))["score__max"] or 0,
            "average_score": user_scores.aggregate(Avg("score"))["score__avg"] or 0,
            "total_plays": user_scores.count(),
            "global_high_score": all_scores.aggregate(Max("score"))["score__max"] or 0,
            "global_average": all_scores.aggregate(Avg("score"))["score__avg"] or 0,
        }
        return Response(stats)

    @action(detail=True, methods=["get"])
    def leaderboard(self, request, pk=None):
        game = self.get_object()
        top_scores = GameScore.objects.filter(game=game).order_by("-score")[:10]
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
        game = serializer.validated_data["game"]
        score = serializer.validated_data["score"]
        achievements = GameAchievement.objects.filter(game=game)

        for achievement in achievements:
            # Başarı kriterleri JSON olabilir ya da metin; güvenli biçimde ayıkla
            criteria_data = {}
            try:
                if isinstance(achievement.criteria, dict):
                    criteria_data = achievement.criteria
                elif (
                    isinstance(achievement.criteria, str)
                    and achievement.criteria.strip()
                ):
                    import json as _json

                    criteria_data = _json.loads(achievement.criteria)
            except Exception:
                criteria_data = {}

            # Örnek: minimum_score kriteri
            min_score = None
            if isinstance(criteria_data, dict) and "minimum_score" in criteria_data:
                try:
                    val = criteria_data.get("minimum_score")
                    if val is not None:
                        min_score = float(val)
                except Exception:
                    min_score = None

            if min_score is not None and score >= min_score:
                UserGameAchievement.objects.get_or_create(
                    user=self.request.user, achievement=achievement
                )


class GameAchievementViewSet(viewsets.ModelViewSet):
    queryset = GameAchievement.objects.all()
    serializer_class = GameAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def my_achievements(self, request):
        user_achievements = UserGameAchievement.objects.filter(user=request.user)
        serializer = UserGameAchievementSerializer(user_achievements, many=True)
        return Response(serializer.data)


class UserGameAchievementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserGameAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserGameAchievement.objects.filter(user=self.request.user)


@login_required
def game_view(request):
    """Oyun ana sayfası"""
    return render(request, "ursina_game/game.html")


@login_required
def start_game(request):
    """Oyunu başlat"""
    game = FinancialTradingGame()
    result = game.start()
    return JsonResponse(
        {
            "status": result.get("status", "success"),
            "message": "Oyun başlatıldı",
            "pid": result.get("pid"),
        }
    )


@login_required
def pause_game(request):
    """Oyunu duraklat"""
    game = FinancialTradingGame()
    result = game.pause()
    return JsonResponse(
        {"status": result.get("status", "success"), "message": "Oyun duraklatıldı"}
    )


@login_required
def resume_game(request):
    """Oyunu devam ettir"""
    game = FinancialTradingGame()
    result = game.resume()
    return JsonResponse(
        {"status": result.get("status", "success"), "message": "Oyun devam ediyor"}
    )


@login_required
def end_game(request):
    """Oyunu bitir"""
    game = FinancialTradingGame()
    result = game.end()
    return JsonResponse(
        {"status": result.get("status", "success"), "message": "Oyun sonlandırıldı"}
    )


class UrsinaPlayerViewSet(viewsets.ModelViewSet):
    queryset = UrsinaPlayer.objects.all()
    serializer_class = UrsinaPlayerSerializer
    permission_classes = [permissions.IsAuthenticated]


class PlayerWalletViewSet(viewsets.ModelViewSet):
    queryset = PlayerWallet.objects.all()
    serializer_class = PlayerWalletSerializer
    permission_classes = [permissions.IsAuthenticated]


class UrsinaGameSessionViewSet(viewsets.ModelViewSet):
    queryset = UrsinaGameSession.objects.all()
    serializer_class = UrsinaGameSessionSerializer
    permission_classes = [permissions.IsAuthenticated]


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [permissions.IsAuthenticated]


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]


class PlayerAchievementViewSet(viewsets.ModelViewSet):
    queryset = PlayerAchievement.objects.all()
    serializer_class = PlayerAchievementSerializer
    permission_classes = [permissions.IsAuthenticated]
