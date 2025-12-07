# -*- coding: utf-8 -*-
from django.urls import path, include
import importlib
from . import views
from .views_esport import (
    player_hub,
    tournaments_list,
    tournament_detail,
    tournament_register,
    quests_page,
    store_page,
    buy_item,
    rankings_page,
    match_history,
    profile_page,
    friends_page,
    teams_page,
)

app_name = "games"

urlpatterns = [
    path("", views.index, name="games_index"),
    # E-Spor merkezi
    path("hub/", player_hub, name="player_hub"),
    path("profile/", profile_page, name="my_profile"),
    path("profile/<str:username>/", profile_page, name="player_profile"),
    # Turnuvalar
    path("tournaments/", tournaments_list, name="tournaments"),
    path(
        "tournament/<int:tournament_id>/", tournament_detail, name="tournament_detail"
    ),
    path(
        "tournament/<int:tournament_id>/register/",
        tournament_register,
        name="tournament_register",
    ),
    # Progression
    path("quests/", quests_page, name="quests"),
    path("görevler/", quests_page, name="gorevler"),  # Turkish alias
    path("quests/bridge/", views.quest_bridge, name="quest_bridge"),
    path("quests/bridge", views.quest_bridge, name="quest_bridge_alias"),
    path("görevler/köprü/", views.quest_bridge, name="gorevler_kopru"),  # Turkish alias
    path("rankings/", rankings_page, name="rankings"),
    path("matches/", match_history, name="match_history"),
    # Ekonomi
    path("store/", store_page, name="store"),
    path("store/buy/<int:item_id>/", buy_item, name="buy_item"),
    # Sosyal
    path("friends/", friends_page, name="friends"),
    path("teams/", teams_page, name="teams"),
    # Mevcut sayfalar
    path("leaderboard/", views.leaderboard_page, name="leaderboard"),
    path("<int:game_id>/", views.detail, name="game_detail"),
    path("accounting/", views.game_accounting, name="game_accounting"),
    path("trading/", views.game_trading, name="game_trading"),
    path("investing/", views.game_investing, name="game_investing"),
    path("social/", views.game_social, name="game_social"),
    path("collection/", views.game_collection, name="game_collection"),
    path("achievements/", views.game_achievements, name="game_achievements"),
    path("inventory/", views.game_inventory, name="game_inventory"),
    path("tax/", views.game_tax, name="game_tax"),
    path("learning/", views.game_learning, name="game_learning"),
    path("market/", views.game_market, name="game_market"),
    # Alt uygulamalar
    path(
        "trade-sim/",
        include(("games.trade_sim.urls", "trade_sim"), namespace="trade_sim"),
    ),
    path(
        "finquest/", include(("games.finquest.urls", "finquest"), namespace="finquest")
    ),
    path(
        "game_app/", include(("games.game_app.urls", "game_app"), namespace="game_app")
    ),
    # API uçları
    path("api/", include(("games.api.urls", "games_api"), namespace="api")),
]

# Opsiyonel: Eski 'ursina_game' uygulaması mevcutsa dahil et (geri uyumluluk)
try:
    importlib.import_module("games.ursina_game.urls")
    urlpatterns.append(
        path(
            "ursina/",
            include(("games.ursina_game.urls", "ursina_game"), namespace="ursina_game"),
        )
    )
except ModuleNotFoundError:
    # Modül yoksa, makemigrations ve server başlatma hataya düşmesin
    pass
