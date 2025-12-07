# -*- coding: utf-8 -*-
"""
FinAsis Games - Admin Panel Configuration
E-Spor yönetimi için gelişmiş admin paneli
"""

from django.contrib import admin
from .models import (
    Game,
    Season,
    Badge,
    PlayerProfile,
    Tournament,
    TournamentParticipant,
    Match,
    DailyQuest,
    PlayerQuest,
    Item,
    PlayerInventory,
    Leaderboard,
    Friend,
    Team,
    TeamMembership,
    GameSession,
)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "game_type",
        "is_esport_enabled",
        "min_players",
        "max_players",
        "duration_minutes",
    ]
    list_filter = ["game_type", "is_esport_enabled"]
    search_fields = ["name", "description"]
    list_editable = ["is_esport_enabled"]


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "start_date",
        "end_date",
        "is_active",
        "is_ongoing",
        "reward_pool",
    ]
    list_filter = ["is_active", "start_date"]
    search_fields = ["name"]
    date_hierarchy = "start_date"


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ["icon", "name", "rarity", "points", "xp_reward"]
    list_filter = ["rarity"]
    search_fields = ["name", "description"]
    ordering = ["-points"]


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "level",
        "rank",
        "elo_rating",
        "total_score",
        "games_won",
        "games_played",
        "daily_streak",
        "coins",
        "gems",
    ]
    list_filter = ["rank", "difficulty", "level"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["created_at", "updated_at", "xp_to_next_level"]

    fieldsets = (
        ("Kullanıcı", {"fields": ("user", "difficulty")}),
        (
            "Progression",
            {
                "fields": (
                    "level",
                    "xp",
                    "xp_to_next_level",
                    "rank",
                    "elo_rating",
                    "mmr",
                )
            },
        ),
        (
            "Beceriler",
            {
                "fields": (
                    "skill_trade",
                    "skill_invest",
                    "skill_budget",
                    "skill_education",
                    "skill_accounting",
                )
            },
        ),
        (
            "İstatistikler",
            {
                "fields": (
                    "games_played",
                    "games_won",
                    "games_lost",
                    "total_score",
                    "highest_score",
                )
            },
        ),
        ("Ekonomi", {"fields": ("coins", "gems")}),
        ("Streak", {"fields": ("daily_streak", "last_played_date")}),
        ("İlişkiler", {"fields": ("badges", "current_season")}),
    )


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "game",
        "tournament_type",
        "status",
        "start_date",
        "participant_count",
        "prize_pool_coins",
    ]
    list_filter = ["tournament_type", "status", "season"]
    search_fields = ["name", "description"]
    date_hierarchy = "start_date"

    def participant_count(self, obj):
        return obj.participants.count()

    participant_count.short_description = "Katılımcı"


@admin.register(TournamentParticipant)
class TournamentParticipantAdmin(admin.ModelAdmin):
    list_display = [
        "player",
        "tournament",
        "seed",
        "final_rank",
        "total_score",
        "registered_at",
    ]
    list_filter = ["tournament"]
    search_fields = ["player__username", "tournament__name"]


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "tournament",
        "game",
        "player1",
        "player2",
        "status",
        "get_score",
        "winner",
        "scheduled_time",
    ]
    list_filter = ["status", "game", "tournament"]
    search_fields = ["player1__username", "player2__username"]
    date_hierarchy = "scheduled_time"

    def get_score(self, obj):
        return f"{obj.player1_score} - {obj.player2_score}"

    get_score.short_description = "Skor"


@admin.register(DailyQuest)
class DailyQuestAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "quest_type",
        "target_value",
        "difficulty_level",
        "reward_xp",
        "reward_coins",
        "is_daily",
    ]
    list_filter = ["quest_type", "is_daily", "is_weekly", "difficulty_level"]
    search_fields = ["title", "description"]


@admin.register(PlayerQuest)
class PlayerQuestAdmin(admin.ModelAdmin):
    list_display = [
        "player",
        "quest",
        "current_value",
        "target_value",
        "is_completed",
        "expires_at",
    ]
    list_filter = ["is_completed", "quest__quest_type"]
    search_fields = ["player__username", "quest__title"]

    def target_value(self, obj):
        return obj.quest.target_value

    target_value.short_description = "Hedef"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "item_type",
        "rarity",
        "price_coins",
        "price_gems",
        "is_tradeable",
        "is_purchasable",
    ]
    list_filter = ["item_type", "rarity", "is_tradeable", "is_purchasable"]
    search_fields = ["name", "description"]


@admin.register(PlayerInventory)
class PlayerInventoryAdmin(admin.ModelAdmin):
    list_display = [
        "player",
        "item",
        "quantity",
        "is_equipped",
        "acquired_at",
        "expires_at",
    ]
    list_filter = ["is_equipped", "item__item_type", "item__rarity"]
    search_fields = ["player__username", "item__name"]


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = [
        "rank",
        "player",
        "leaderboard_type",
        "game",
        "season",
        "score",
        "updated_at",
    ]
    list_filter = ["leaderboard_type", "game", "season"]
    search_fields = ["player__username"]
    ordering = ["rank"]


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ["from_player", "to_player", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["from_player__username", "to_player__username"]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = [
        "tag",
        "name",
        "owner",
        "team_rank",
        "team_elo",
        "member_count",
        "created_at",
    ]
    search_fields = ["name", "tag"]
    list_filter = ["team_rank"]

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = "Üye Sayısı"


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ["team", "player", "role", "joined_at"]
    list_filter = ["role", "team"]
    search_fields = ["player__username", "team__name"]


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "player",
        "game",
        "score",
        "is_victory",
        "duration_seconds",
        "xp_earned",
        "coins_earned",
        "started_at",
    ]
    list_filter = ["game", "is_victory"]
    search_fields = ["player__username"]
    date_hierarchy = "started_at"
