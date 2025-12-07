"""
E-Spor özellikleri için view'lar
Turnuva, Sıralama, Progression, Quests
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import (
    Tournament,
    TournamentParticipant,
    Match,
    PlayerProfile,
    PlayerQuest,
    Item,
    PlayerInventory,
    Leaderboard,
    Friend,
    Team,
)


@login_required
def player_hub(request):
    """Oyuncu merkezi - ana e-spor dashboard"""
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    profile.check_daily_streak()

    # XP progress yüzdesi
    xp_percentage = (
        int((profile.xp / profile.xp_to_next_level) * 100)
        if profile.xp_to_next_level > 0
        else 0
    )

    # Günlük quest'ler
    today = timezone.now().date()
    today + timedelta(days=1)
    daily_quests = PlayerQuest.objects.filter(
        player=request.user, expires_at__gte=timezone.now(), is_completed=False
    )[:3]

    # Aktif turnuvalar
    active_tournaments = Tournament.objects.filter(
        status__in=["registration", "ongoing"], end_date__gte=timezone.now()
    )[:3]

    # Son maçlar
    recent_matches = Match.objects.filter(
        Q(player1=request.user) | Q(player2=request.user)
    ).order_by("-ended_at")[:5]

    # Sıralama
    try:
        leaderboard_entry = Leaderboard.objects.get(
            player=request.user, leaderboard_type="global"
        )
        global_rank = leaderboard_entry.rank
    except Leaderboard.DoesNotExist:
        global_rank = None

    context = {
        "profile": profile,
        "xp_percentage": xp_percentage,
        "daily_quests": daily_quests,
        "active_tournaments": active_tournaments,
        "recent_matches": recent_matches,
        "global_rank": global_rank,
    }

    return render(request, "games/player_hub.html", context)


@login_required
def tournaments_list(request):
    """Turnuva listesi"""
    active = Tournament.objects.filter(status__in=["registration", "ongoing"]).order_by(
        "start_date"
    )
    upcoming = Tournament.objects.filter(status="upcoming").order_by("start_date")[:5]
    finished = Tournament.objects.filter(status="finished").order_by("-end_date")[:10]

    # Oyuncunun katıldığı turnuvalar
    my_tournaments = TournamentParticipant.objects.filter(
        player=request.user
    ).select_related("tournament")[:5]

    context = {
        "active_tournaments": active,
        "upcoming_tournaments": upcoming,
        "finished_tournaments": finished,
        "my_tournaments": my_tournaments,
    }

    return render(request, "games/tournaments.html", context)


@login_required
def tournament_detail(request, tournament_id):
    """Turnuva detay ve kayıt"""
    tournament = get_object_or_404(Tournament, id=tournament_id)
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)

    # Kayıt olmuş mu?
    is_registered = TournamentParticipant.objects.filter(
        tournament=tournament, player=request.user
    ).exists()

    # Katılabilir mi?
    can_register = (
        tournament.status == "registration"
        and not is_registered
        and tournament.participants.count() < tournament.max_participants
        and profile.coins >= tournament.entry_fee_coins
        and profile.gems >= tournament.entry_fee_gems
    )

    participants = tournament.participants.select_related("player").order_by("seed")
    matches = tournament.matches.select_related(
        "player1", "player2", "winner"
    ).order_by("-scheduled_time")

    context = {
        "tournament": tournament,
        "is_registered": is_registered,
        "can_register": can_register,
        "participants": participants,
        "matches": matches,
    }

    return render(request, "games/tournament_detail.html", context)


@login_required
def tournament_register(request, tournament_id):
    """Turnuvaya kayıt ol"""
    tournament = get_object_or_404(Tournament, id=tournament_id)
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Kontroller
        if tournament.status != "registration":
            return redirect("games:tournament_detail", tournament_id=tournament_id)

        if tournament.participants.count() >= tournament.max_participants:
            return redirect("games:tournament_detail", tournament_id=tournament_id)

        # Ücret kontrolü
        if (
            profile.coins < tournament.entry_fee_coins
            or profile.gems < tournament.entry_fee_gems
        ):
            return redirect("games:tournament_detail", tournament_id=tournament_id)

        # Kayıt oluştur
        TournamentParticipant.objects.create(tournament=tournament, player=request.user)

        # Ücreti kes
        profile.coins -= tournament.entry_fee_coins
        profile.gems -= tournament.entry_fee_gems
        profile.save(update_fields=["coins", "gems"])

    return redirect("games:tournament_detail", tournament_id=tournament_id)


@login_required
def quests_page(request):
    """Günlük görevler sayfası"""
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)

    # Aktif quest'ler
    active_quests = PlayerQuest.objects.filter(
        player=request.user, is_completed=False, expires_at__gte=timezone.now()
    ).select_related("quest")

    # Tamamlananlar (son 10)
    completed_quests = (
        PlayerQuest.objects.filter(player=request.user, is_completed=True)
        .select_related("quest")
        .order_by("-completed_at")[:10]
    )

    context = {
        "profile": profile,
        "active_quests": active_quests,
        "completed_quests": completed_quests,
    }

    return render(request, "games/quests.html", context)


@login_required
def store_page(request):
    """Oyun içi mağaza"""
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)

    items = Item.objects.filter(is_purchasable=True).order_by("rarity", "price_coins")

    # Oyuncunun envanteri
    my_inventory = PlayerInventory.objects.filter(player=request.user).select_related(
        "item"
    )

    context = {
        "profile": profile,
        "items": items,
        "my_inventory": my_inventory,
    }

    return render(request, "games/store.html", context)


@login_required
def buy_item(request, item_id):
    """Eşya satın al"""
    if request.method == "POST":
        item = get_object_or_404(Item, id=item_id, is_purchasable=True)
        profile, _ = PlayerProfile.objects.get_or_create(user=request.user)

        # Yeterli para var mı?
        if profile.coins >= item.price_coins and profile.gems >= item.price_gems:
            # Parayı kes
            profile.coins -= item.price_coins
            profile.gems -= item.price_gems
            profile.save(update_fields=["coins", "gems"])

            # Envantere ekle
            inventory, created = PlayerInventory.objects.get_or_create(
                player=request.user, item=item, defaults={"quantity": 1}
            )
            if not created:
                inventory.quantity += 1
                inventory.save()

            # Eğer süreliyse, bitiş tarihi belirle
            if item.duration_hours > 0:
                inventory.expires_at = timezone.now() + timedelta(
                    hours=item.duration_hours
                )
                inventory.save()

    return redirect("games:store")


@login_required
def rankings_page(request):
    """Sıralama tabloları"""
    # Global sıralama
    global_rankings = (
        Leaderboard.objects.filter(leaderboard_type="global")
        .select_related("player")
        .order_by("rank")[:100]
    )

    # Haftalık
    weekly_rankings = (
        Leaderboard.objects.filter(leaderboard_type="weekly")
        .select_related("player")
        .order_by("rank")[:50]
    )

    # Oyuncunun sıralaması
    try:
        my_rank = Leaderboard.objects.get(
            player=request.user, leaderboard_type="global"
        )
    except Leaderboard.DoesNotExist:
        my_rank = None

    context = {
        "global_rankings": global_rankings,
        "weekly_rankings": weekly_rankings,
        "my_rank": my_rank,
    }

    return render(request, "games/rankings.html", context)


@login_required
def match_history(request):
    """Maç geçmişi"""
    matches = (
        Match.objects.filter(Q(player1=request.user) | Q(player2=request.user))
        .select_related("game", "player1", "player2", "winner")
        .order_by("-ended_at")[:50]
    )

    # İstatistikler
    total_matches = matches.count()
    wins = matches.filter(winner=request.user).count()
    losses = total_matches - wins
    win_rate = int((wins / total_matches) * 100) if total_matches > 0 else 0

    context = {
        "matches": matches,
        "stats": {
            "total": total_matches,
            "wins": wins,
            "losses": losses,
            "win_rate": win_rate,
        },
    }

    return render(request, "games/match_history.html", context)


@login_required
def profile_page(request, username=None):
    """Oyuncu profil sayfası (kendi veya başkası)"""
    if username:
        from django.contrib.auth import get_user_model

        User = get_user_model()
        player = get_object_or_404(User, username=username)
    else:
        player = request.user

    profile, _ = PlayerProfile.objects.get_or_create(user=player)

    # Rozetler
    badges = profile.badges.all()

    # İstatistikler
    total_matches = Match.objects.filter(
        Q(player1=player) | Q(player2=player), status="finished"
    ).count()

    # Son maçlar
    recent_matches = Match.objects.filter(
        Q(player1=player) | Q(player2=player)
    ).order_by("-ended_at")[:10]

    context = {
        "viewed_player": player,
        "profile": profile,
        "badges": badges,
        "total_matches": total_matches,
        "recent_matches": recent_matches,
        "is_own_profile": player == request.user,
    }

    return render(request, "games/profile.html", context)


@login_required
def friends_page(request):
    """Arkadaşlar sayfası"""
    # Arkadaşlar
    friends = Friend.objects.filter(
        Q(from_player=request.user, status="accepted")
        | Q(to_player=request.user, status="accepted")
    ).select_related("from_player", "to_player")

    # Bekleyen istekler
    pending_requests = Friend.objects.filter(
        to_player=request.user, status="pending"
    ).select_related("from_player")

    context = {
        "friends": friends,
        "pending_requests": pending_requests,
    }

    return render(request, "games/friends.html", context)


@login_required
def teams_page(request):
    """Takımlar sayfası"""
    # Oyuncunun takımları
    my_teams = request.user.teams.all()

    # Top takımlar
    top_teams = Team.objects.order_by("-team_elo")[:20]

    context = {
        "my_teams": my_teams,
        "top_teams": top_teams,
    }

    return render(request, "games/teams.html", context)
