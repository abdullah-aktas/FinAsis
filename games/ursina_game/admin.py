from django.contrib import admin
from .models import Game, GameScore, GameAchievement, UserGameAchievement

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'game_type', 'difficulty', 'max_score')
    list_filter = ('game_type', 'difficulty')
    search_fields = ('title', 'description')

@admin.register(GameScore)
class GameScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'score', 'completion_percentage', 'played_at')
    list_filter = ('game', 'played_at')
    search_fields = ('user__username', 'game__title')

@admin.register(GameAchievement)
class GameAchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'points')
    list_filter = ('game',)
    search_fields = ('title', 'description')

@admin.register(UserGameAchievement)
class UserGameAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('achievement__game', 'earned_at')
    search_fields = ('user__username', 'achievement__title')
