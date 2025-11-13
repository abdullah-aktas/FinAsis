"""
TradeSim Zorluk API Endpoints
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .difficulty_system import (
    DifficultyLevel, DIFFICULTY_CONFIGS, DifficultyManager,
    get_available_difficulties, get_recommended_difficulty, DIFFICULTY_UNLOCK_REQUIREMENTS
)
from games.models import PlayerProfile


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_game_with_difficulty(request):
    """
    Oyunu belirli bir zorluk seviyesiyle başlat
    POST /games/trade-sim/api/start/
    Body: {
        "difficulty": 3,  // DifficultyLevel value
        "character_name": "Trader"
    }
    """
    difficulty_value = request.data.get('difficulty', 3)
    character_name = request.data.get('character_name', f'{request.user.username} Trader')
    
    # Zorluk seviyesini al
    try:
        difficulty_level = DifficultyLevel(difficulty_value)
        config = DIFFICULTY_CONFIGS[difficulty_level]
    except (ValueError, KeyError):
        return Response({'error': 'Geçersiz zorluk seviyesi'}, status=400)
    
    # Oyuncu profili
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    
    # Zorluk kilidi kontrolü
    available = get_available_difficulties(profile.level, profile.elo_rating)
    if difficulty_level not in available:
        return Response({
            'error': 'Bu zorluk seviyesi kilitli',
            'requirements': {
                'min_level': DIFFICULTY_UNLOCK_REQUIREMENTS[difficulty_level]['min_level'],
                'min_elo': DIFFICULTY_UNLOCK_REQUIREMENTS[difficulty_level]['min_elo'],
                'your_level': profile.level,
                'your_elo': profile.elo_rating,
            }
        }, status=403)
    
    # Karakter oluştur/güncelle
    from .models import Character, City
    default_city = City.objects.first()
    
    character, created = Character.objects.get_or_create(
        user=request.user,
        defaults={
            'name': character_name,
            'city': default_city,
        }
    )
    
    # Oyun session'ı başlat
    difficulty_manager = DifficultyManager(difficulty_level)
    
    starting_capital = 10000
    victory_requirement = difficulty_manager.get_victory_requirement(starting_capital)
    
    game_session_data = {
        'character_id': character.id,
        'difficulty': difficulty_level.value,
        'difficulty_name': config.name,
        'starting_capital': starting_capital,
        'victory_requirement': victory_requirement,
        'time_limit_minutes': config.time_limit_minutes,
        'ai_count': config.ai_count,
        'ai_intelligence': config.ai_intelligence,
        'current_capital': starting_capital,
        'turn': 0,
        'active_events': [],
        'multipliers': {
            'xp': config.xp_multiplier,
            'coins': config.coin_multiplier,
            'elo': config.elo_gain_multiplier,
        }
    }
    
    # Session'ı kaydet (önbellekte veya veritabanında)
    request.session['tradesim_game_session'] = game_session_data
    
    return Response({
        'success': True,
        'game_session': game_session_data,
        'message': f'{config.name} modunda oyun başladı! Hedef: {victory_requirement} altın',
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_difficulty_info(request):
    """
    Mevcut zorluk bilgileri ve kilitli seviyeler
    GET /games/trade-sim/api/difficulty/info/
    """
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    
    available = get_available_difficulties(profile.level, profile.elo_rating)
    
    # Win rate hesapla
    win_rate = profile.games_won / profile.games_played if profile.games_played > 0 else 0.5
    recommended = get_recommended_difficulty(profile.level, profile.elo_rating, win_rate)
    
    difficulties = []
    for diff_level in DifficultyLevel:
        config = DIFFICULTY_CONFIGS[diff_level]
        requirements = DIFFICULTY_UNLOCK_REQUIREMENTS[diff_level]
        is_unlocked = diff_level in available
        
        difficulties.append({
            'value': diff_level.value,
            'code': diff_level.name.lower(),
            'name': config.name,
            'description': config.description,
            'is_unlocked': is_unlocked,
            'is_recommended': diff_level == recommended,
            'requirements': {
                'min_level': requirements['min_level'],
                'min_elo': requirements['min_elo'],
            },
            'stats': {
                'ai_count': config.ai_count,
                'ai_intelligence': f'{int(config.ai_intelligence * 100)}%',
                'time_limit': f'{config.time_limit_minutes} dk',
                'volatility': f'{int(config.price_volatility * 100)}%',
            },
            'rewards': {
                'xp_multiplier': f'{config.xp_multiplier}x',
                'coin_multiplier': f'{config.coin_multiplier}x',
                'elo_multiplier': f'{config.elo_gain_multiplier}x',
            }
        })
    
    return Response({
        'player': {
            'level': profile.level,
            'elo': profile.elo_rating,
            'rank': profile.rank,
            'games_played': profile.games_played,
            'games_won': profile.games_won,
            'win_rate': f'{int(win_rate * 100)}%',
        },
        'difficulties': difficulties,
        'recommended_difficulty': recommended.value,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finish_game_with_rewards(request):
    """
    Oyun bittikten sonra ödülleri hesapla ve kaydet
    POST /games/trade-sim/api/finish/
    Body: {
        "score": 25000,
        "final_capital": 35000,
        "difficulty": 3,
        "is_victory": true,
        "turns_taken": 45,
        "trades_made": 120
    }
    """
    score = request.data.get('score', 0)
    final_capital = request.data.get('final_capital', 0)
    difficulty_value = request.data.get('difficulty', 3)
    is_victory = request.data.get('is_victory', False)
    turns_taken = request.data.get('turns_taken', 0)
    trades_made = request.data.get('trades_made', 0)
    
    # Zorluk config
    try:
        difficulty_level = DifficultyLevel(difficulty_value)
        difficulty_manager = DifficultyManager(difficulty_level)
    except ValueError:
        return Response({'error': 'Geçersiz zorluk'}, status=400)
    
    # Ödülleri hesapla
    rewards = difficulty_manager.get_rewards(score, is_victory)
    
    # Profil güncelle
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    
    profile.add_xp(rewards['xp'])
    profile.coins += rewards['coins']
    profile.games_played += 1
    
    if is_victory:
        profile.games_won += 1
        profile.elo_rating += rewards['elo_change']
    else:
        profile.games_lost += 1
        profile.elo_rating += rewards['elo_change']  # Negatif olacak
    
    # ELO'ya göre rank güncelle
    profile.update_rank()
    
    if score > profile.highest_score:
        profile.highest_score = score
    
    profile.total_score += score
    profile.save(update_fields=[
        'games_played', 'games_won', 'games_lost', 
        'elo_rating', 'highest_score', 'total_score'
    ])
    
    # Beceri güncelle (TradeSim için trade skill)
    if is_victory:
        profile.skill_trade = min(100, profile.skill_trade + (2 * difficulty_level.value))
    else:
        profile.skill_trade = max(0, profile.skill_trade - 1)
    
    profile.save(update_fields=['skill_trade'])
    
    # GameSession kaydet
    from games.models import GameSession, Game
    
    tradesim_game, _ = Game.objects.get_or_create(
        name='TradeSim',
        defaults={
            'description': 'Şehirler arası ticaret simülasyonu',
            'game_type': 'simulation',
            'is_esport_enabled': True,
        }
    )
    
    session = GameSession.objects.create(
        player=request.user,
        game=tradesim_game,
        score=score,
        is_victory=is_victory,
        xp_earned=rewards['xp'],
        coins_earned=rewards['coins'],
        duration_seconds=turns_taken * 30,  # Yaklaşık
        session_data={
            'difficulty': difficulty_level.name,
            'final_capital': final_capital,
            'turns': turns_taken,
            'trades': trades_made,
        }
    )
    
    return Response({
        'success': True,
        'rewards': {
            'xp': rewards['xp'],
            'coins': rewards['coins'],
            'elo_change': rewards['elo_change'],
        },
        'new_stats': {
            'level': profile.level,
            'elo': profile.elo_rating,
            'rank': profile.rank,
            'coins': profile.coins,
            'skill_trade': profile.skill_trade,
        },
        'session_id': session.id,
    })

