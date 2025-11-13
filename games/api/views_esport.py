"""
E-Spor API endpoints
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from ..models import (
    PlayerProfile, DailyQuest, PlayerQuest, Match, 
    GameSession, Item, PlayerInventory
)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def record_game_session(request):
    """
    Oyun oturumunu kaydet ve ödülleri hesapla
    POST /games/api/session/record/
    Body: {
        "game_id": 1,
        "score": 5000,
        "is_victory": true,
        "duration_seconds": 600,
        "session_data": {}
    }
    """
    from ..models import Game
    
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    profile.check_daily_streak()
    
    game_id = request.data.get('game_id')
    score = int(request.data.get('score', 0))
    is_victory = request.data.get('is_victory', False)
    duration_seconds = int(request.data.get('duration_seconds', 0))
    session_data = request.data.get('session_data', {})
    
    try:
        game = Game.objects.get(id=game_id)
    except Game.DoesNotExist:
        return Response({'error': 'Oyun bulunamadi'}, status=404)
    
    # XP hesapla (skor tabanlı)
    base_xp = score // 100
    victory_bonus = 200 if is_victory else 0
    streak_bonus = profile.daily_streak * 10
    total_xp = base_xp + victory_bonus + streak_bonus
    
    # Coin hesapla
    base_coins = score // 50
    coins_earned = base_coins + (100 if is_victory else 0)
    
    # Session kaydet
    session = GameSession.objects.create(
        player=request.user,
        game=game,
        started_at=timezone.now() - timedelta(seconds=duration_seconds),
        ended_at=timezone.now(),
        duration_seconds=duration_seconds,
        score=score,
        is_victory=is_victory,
        xp_earned=total_xp,
        coins_earned=coins_earned,
        session_data=session_data
    )
    
    # Profil güncelle
    profile.add_xp(total_xp)
    profile.coins += coins_earned
    profile.games_played += 1
    if is_victory:
        profile.games_won += 1
    else:
        profile.games_lost += 1
    
    if score > profile.highest_score:
        profile.highest_score = score
    
    profile.total_score += score
    profile.save(update_fields=['coins', 'games_played', 'games_won', 'games_lost', 'highest_score', 'total_score'])
    
    # Quest'leri güncelle
    update_quests(request.user, 'play_games', 1)
    if is_victory:
        update_quests(request.user, 'win_games', 1)
    update_quests(request.user, 'earn_score', score)
    
    return Response({
        'success': True,
        'xp_earned': total_xp,
        'coins_earned': coins_earned,
        'level': profile.level,
        'xp': profile.xp,
        'xp_to_next': profile.xp_to_next_level,
        'total_coins': profile.coins,
        'daily_streak': profile.daily_streak,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_daily_quests(request):
    """
    Günlük görevleri getir, yoksa ata
    GET /games/api/quests/daily/
    """
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    
    # Bugünün quest'leri
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # Mevcut aktif quest'ler
    active = PlayerQuest.objects.filter(
        player=request.user,
        expires_at__gte=timezone.now(),
        assigned_at__gte=today_start
    ).select_related('quest')
    
    # Eğer 3'ten azsa, yeni quest ata
    if active.count() < 3:
        available_quests = DailyQuest.objects.filter(is_daily=True).order_by('?')[:3]
        for quest in available_quests:
            # Bugün bu quest zaten atanmış mı?
            if not PlayerQuest.objects.filter(
                player=request.user,
                quest=quest,
                assigned_at__gte=today_start
            ).exists():
                PlayerQuest.objects.create(
                    player=request.user,
                    quest=quest,
                    expires_at=today_end
                )
        
        # Yeniden getir
        active = PlayerQuest.objects.filter(
            player=request.user,
            expires_at__gte=timezone.now()
        ).select_related('quest')
    
    quests_data = []
    for pq in active:
        quests_data.append({
            'id': pq.id,
            'title': pq.quest.title,
            'description': pq.quest.description,
            'type': pq.quest.quest_type,
            'current': pq.current_value,
            'target': pq.quest.target_value,
            'progress': int((pq.current_value / pq.quest.target_value) * 100),
            'is_completed': pq.is_completed,
            'rewards': {
                'xp': pq.quest.reward_xp,
                'coins': pq.quest.reward_coins,
                'gems': pq.quest.reward_gems,
            }
        })
    
    return Response({
        'quests': quests_data,
        'profile': {
            'level': profile.level,
            'coins': profile.coins,
            'gems': profile.gems,
            'streak': profile.daily_streak,
        }
    })


def update_quests(player, quest_type, increment=1):
    """Quest ilerlemesini güncelle"""
    active_quests = PlayerQuest.objects.filter(
        player=player,
        quest__quest_type=quest_type,
        is_completed=False,
        expires_at__gte=timezone.now()
    )
    
    for pq in active_quests:
        pq.current_value += increment
        pq.save()
        pq.check_completion()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile_stats(request):
    """
    Oyuncu istatistiklerini getir
    GET /games/api/profile/stats/
    """
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    
    # Win rate hesapla
    total_games = profile.games_played
    win_rate = int((profile.games_won / total_games) * 100) if total_games > 0 else 0
    
    return Response({
        'level': profile.level,
        'xp': profile.xp,
        'xp_to_next': profile.xp_to_next_level,
        'xp_percentage': int((profile.xp / profile.xp_to_next_level) * 100) if profile.xp_to_next_level > 0 else 0,
        'rank': profile.rank,
        'elo': profile.elo_rating,
        'coins': profile.coins,
        'gems': profile.gems,
        'total_score': profile.total_score,
        'games_played': profile.games_played,
        'games_won': profile.games_won,
        'games_lost': profile.games_lost,
        'win_rate': win_rate,
        'daily_streak': profile.daily_streak,
        'badges_count': profile.badges.count(),
    })

