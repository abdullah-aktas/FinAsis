"""
FinQuest 3D Admin Panel
"""
from django.contrib import admin
from .models import (
    FinQuestCharacter,
    FinQuestItem,
    FinQuestInventory,
    FinQuestQuest,
    FinQuestPlayerQuest,
    FinQuestNPC,
    FinQuestWorld,
    FinQuestEvent,
    FinQuestSession,
)


@admin.register(FinQuestCharacter)
class FinQuestCharacterAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "user",
        "level",
        "current_city",
        "money",
        "difficulty",
        "last_played",
    ]
    list_filter = ["difficulty", "current_city", "level"]
    search_fields = ["name", "user__username"]

    fieldsets = (
        ("Temel Bilgiler", {"fields": ("user", "name", "difficulty")}),
        (
            "Lokasyon",
            {"fields": ("current_city", "position_x", "position_y", "position_z")},
        ),
        ("İstatistikler", {"fields": ("level", "xp", "health", "energy", "money")}),
        (
            "Beceriler",
            {
                "fields": (
                    "skill_trading",
                    "skill_negotiation",
                    "skill_accounting",
                    "skill_investing",
                    "skill_management",
                )
            },
        ),
        (
            "Progression",
            {
                "fields": (
                    "quests_completed",
                    "cities_explored",
                    "achievements_unlocked",
                )
            },
        ),
    )


@admin.register(FinQuestItem)
class FinQuestItemAdmin(admin.ModelAdmin):
    list_display = [
        "icon",
        "name",
        "item_type",
        "buy_price",
        "sell_price",
        "is_tradeable",
    ]
    list_filter = ["item_type", "is_tradeable", "is_stackable"]
    search_fields = ["name", "description"]


@admin.register(FinQuestInventory)
class FinQuestInventoryAdmin(admin.ModelAdmin):
    list_display = ["character", "item", "quantity", "is_equipped"]
    list_filter = ["is_equipped", "item__item_type"]
    search_fields = ["character__name", "item__name"]


@admin.register(FinQuestQuest)
class FinQuestQuestAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "quest_type",
        "required_level",
        "difficulty_level",
        "reward_xp",
        "reward_money",
        "is_active",
    ]
    list_filter = ["quest_type", "difficulty_level", "is_active"]
    search_fields = ["title", "description"]


@admin.register(FinQuestPlayerQuest)
class FinQuestPlayerQuestAdmin(admin.ModelAdmin):
    list_display = ["character", "quest", "is_completed", "started_at", "completed_at"]
    list_filter = ["is_completed", "quest__quest_type"]
    search_fields = ["character__name", "quest__title"]


@admin.register(FinQuestNPC)
class FinQuestNPCAdmin(admin.ModelAdmin):
    list_display = ["name", "npc_type", "city", "ai_intelligence", "personality"]
    list_filter = ["npc_type", "city"]
    search_fields = ["name"]


@admin.register(FinQuestWorld)
class FinQuestWorldAdmin(admin.ModelAdmin):
    list_display = ["name", "economic_level", "tax_rate", "weather", "is_unlocked"]
    list_filter = ["is_unlocked", "economic_level", "weather"]
    search_fields = ["name", "description"]


@admin.register(FinQuestEvent)
class FinQuestEventAdmin(admin.ModelAdmin):
    list_display = ["title", "event_type", "probability", "duration_minutes"]
    list_filter = ["event_type"]
    search_fields = ["title", "description"]


@admin.register(FinQuestSession)
class FinQuestSessionAdmin(admin.ModelAdmin):
    list_display = [
        "character",
        "started_at",
        "duration_seconds",
        "xp_earned",
        "money_earned",
        "quests_completed",
    ]
    list_filter = ["character"]
    date_hierarchy = "started_at"
