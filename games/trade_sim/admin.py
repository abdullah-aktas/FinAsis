from django.contrib import admin
from .models import (
    City,
    Character,
    Quest,
    CharacterQuest,
    Tournament,
    TournamentEntry,
    GameNotification,
    ChatMessage,
    QrReward,
    UserQrReward,
)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "market_size")
    search_fields = ("name",)
    filter_horizontal = ("neighbors",)


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "city", "level", "score")
    search_fields = ("name", "user__username")
    list_filter = ("city", "level")


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ("name", "quest_type", "is_active")
    search_fields = ("name",)
    list_filter = ("quest_type", "is_active")


@admin.register(CharacterQuest)
class CharacterQuestAdmin(admin.ModelAdmin):
    list_display = ("character", "quest", "is_completed", "started_at", "completed_at")
    search_fields = ("character__name", "quest__name")
    list_filter = ("is_completed",)


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "start_time", "end_time", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(TournamentEntry)
class TournamentEntryAdmin(admin.ModelAdmin):
    list_display = (
        "tournament",
        "character",
        "score",
        "rank",
        "reward_claimed",
        "joined_at",
    )
    search_fields = ("tournament__name", "character__name")
    list_filter = ("tournament", "reward_claimed")


@admin.register(GameNotification)
class GameNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "notification_type", "created_at", "is_read")
    search_fields = ("user__username", "message")
    list_filter = ("notification_type", "is_read")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "room",
        "message",
        "created_at",
        "is_deleted",
        "is_reported",
    )
    search_fields = ("user__username", "room", "message")
    list_filter = ("room", "is_deleted", "is_reported")


@admin.register(QrReward)
class QrRewardAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "reward", "is_active")
    search_fields = ("code", "description")
    list_filter = ("is_active",)


@admin.register(UserQrReward)
class UserQrRewardAdmin(admin.ModelAdmin):
    list_display = ("user", "qr_reward", "claimed_at")
    search_fields = ("user__username", "qr_reward__code")
    list_filter = ("claimed_at",)
