# -*- coding: utf-8 -*-
"""
FinQuest 3D Views
Modern 3D web-based finansal macera oyunu
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone


def play(request):
    """FinQuest 3D ana oyun sayfası"""
    character_level = 1
    character_money = 10000
    character_xp = 0
    
    if request.user.is_authenticated:
        from games.models import PlayerProfile
        profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
        character_level = profile.level
        character_money = profile.coins
        character_xp = profile.xp
    
    context = {
        'character_level': character_level,
        'character_money': character_money,
        'character_xp': character_xp,
    }
    
    return render(request, 'finquest/game.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start(request):
    """Oyunu başlat"""
    difficulty = request.data.get('difficulty', 2)
    
    from games.models import PlayerProfile
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    
    return Response({
        'success': True,
        'character': {
            'name': f'{request.user.username} Maceraperest',
            'level': profile.level,
            'health': 100,
            'energy': 100,
            'money': profile.coins,
            'position': {'x': 0, 'y': 1.6, 'z': 0},
        },
        'difficulty': difficulty,
        'world': {
            'name': 'Mardin',
            'time': 'day',
            'weather': 'sunny',
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pause(request):
    """Oyunu duraklat"""
    return Response({'success': True, 'status': 'paused'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resume(request):
    """Oyunu devam ettir"""
    return Response({'success': True, 'status': 'resumed'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end(request):
    """Oyunu bitir ve ödülleri kaydet"""
    xp_earned = request.data.get('xp_earned', 0)
    money_earned = request.data.get('money_earned', 0)
    quests_completed = request.data.get('quests_completed', 0)
    duration_seconds = request.data.get('duration_seconds', 0)
    
    from games.models import PlayerProfile, GameSession, Game
    
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    
    # XP ve para ekle
    profile.add_xp(xp_earned)
    profile.coins += money_earned
    profile.save(update_fields=['coins'])
    
    # Session kaydet
    finquest_game, _ = Game.objects.get_or_create(
        name='FinQuest 3D',
        defaults={
            'description': '3D açık dünya finansal macera',
            'game_type': 'simulation',
            'is_esport_enabled': False,
        }
    )
    
    session = GameSession.objects.create(
        player=request.user,
        game=finquest_game,
        score=money_earned,
        is_victory=quests_completed > 0,
        xp_earned=xp_earned,
        coins_earned=money_earned,
        duration_seconds=duration_seconds,
        session_data={
            'quests_completed': quests_completed,
        }
    )
    
    return Response({
        'success': True,
        'rewards': {
            'xp': xp_earned,
            'coins': money_earned,
        },
        'new_level': profile.level,
        'total_coins': profile.coins,
        'session_id': session.id,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def status(request):
    """Oyun durumu"""
    return Response({'status': 'active', 'timestamp': timezone.now()})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restart(request):
    """Oyunu yeniden başlat"""
    return Response({'success': True, 'message': 'Oyun yeniden başlatıldı'})
