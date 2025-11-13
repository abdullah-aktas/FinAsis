from django.urls import path
from .views import (
    earn_badge,
    save_simulation_score,
    personalize,
    track,
    leaderboard,
    badges_list,
)
from .views_esport import (
    record_game_session,
    get_daily_quests,
    get_profile_stats,
)

urlpatterns = [
    # Mevcut API'ler
    path('badge/earn/', earn_badge, name='earn_badge'),
    path('badges/', badges_list, name='badges_list'),
    path('leaderboard/', leaderboard, name='leaderboard'),
    path('simulation/score/', save_simulation_score, name='save_simulation_score'),
    path('personalize/', personalize, name='personalize'),
    path('track/', track, name='track'),
    
    # E-Spor API'leri
    path('session/record/', record_game_session, name='record_session'),
    path('quests/daily/', get_daily_quests, name='daily_quests'),
    path('profile/stats/', get_profile_stats, name='profile_stats'),
] 