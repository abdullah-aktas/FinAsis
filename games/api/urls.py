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
from .views_social import (
    send_friend_request,
    accept_friend_request,
    reject_friend_request,
    remove_friend,
    search_users,
    create_team,
    join_team,
    leave_team,
)

urlpatterns = [
    # Mevcut API'ler
    path("badge/earn/", earn_badge, name="earn_badge"),
    path("badges/", badges_list, name="badges_list"),
    path("leaderboard/", leaderboard, name="leaderboard"),
    path("simulation/score/", save_simulation_score, name="save_simulation_score"),
    path("personalize/", personalize, name="personalize"),
    path("track/", track, name="track"),
    # E-Spor API'leri
    path("session/record/", record_game_session, name="record_session"),
    path("quests/daily/", get_daily_quests, name="daily_quests"),
    path("profile/stats/", get_profile_stats, name="profile_stats"),
    # Sosyal API'leri
    path("friends/send/", send_friend_request, name="send_friend_request"),
    path("friends/accept/", accept_friend_request, name="accept_friend_request"),
    path("friends/reject/", reject_friend_request, name="reject_friend_request"),
    path("friends/remove/", remove_friend, name="remove_friend"),
    path("friends/search/", search_users, name="search_users"),
    path("teams/create/", create_team, name="create_team"),
    path("teams/join/", join_team, name="join_team"),
    path("teams/leave/", leave_team, name="leave_team"),
]
