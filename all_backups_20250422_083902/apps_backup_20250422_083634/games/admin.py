from django.contrib import admin
from .models import Game, Player, Transaction, Challenge, PlayerChallenge

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'game', 'current_balance', 'score', 'is_active')
    list_filter = ('is_active', 'game')
    search_fields = ('user__username', 'company_name')
    raw_id_fields = ('user', 'game')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('player', 'transaction_type', 'amount', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('player__company_name', 'description')
    raw_id_fields = ('player',)
    date_hierarchy = 'created_at'

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'game', 'points', 'is_completed')
    list_filter = ('is_completed', 'game')
    search_fields = ('title', 'description')
    raw_id_fields = ('game',)

@admin.register(PlayerChallenge)
class PlayerChallengeAdmin(admin.ModelAdmin):
    list_display = ('player', 'challenge', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'completed_at')
    search_fields = ('player__company_name', 'challenge__title')
    raw_id_fields = ('player', 'challenge')
    date_hierarchy = 'completed_at' 