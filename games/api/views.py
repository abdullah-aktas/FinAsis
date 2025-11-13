from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext as _
from django.db.models import Q

from ..ai.personalization import recommend_settings, track_event
from ..models import PlayerProfile, Badge


@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard(request):
    """
    Liderlik tablosunu döndürür: en yüksek skorlu oyuncular.
    Query: ?limit=10
    """
    limit = int(request.query_params.get('limit', 10))
    top_players = PlayerProfile.objects.select_related('user').order_by('-total_score', '-games_played')[:limit]
    
    leaderboard_data = []
    for rank, profile in enumerate(top_players, start=1):
        leaderboard_data.append({
            'rank': rank,
            'username': profile.user.username,
            'score': profile.total_score,
            'games_played': profile.games_played,
            'badge_count': profile.badges.count(),
        })
    
    # Kullanıcı kendi sıralamasını görmek isterse
    user_rank = None
    if request.user.is_authenticated:
        try:
            user_profile = request.user.player_profile
            higher_count = PlayerProfile.objects.filter(
                Q(total_score__gt=user_profile.total_score) |
                (Q(total_score=user_profile.total_score) & Q(games_played__gt=user_profile.games_played))
            ).count()
            user_rank = {
                'rank': higher_count + 1,
                'username': user_profile.user.username,
                'score': user_profile.total_score,
                'games_played': user_profile.games_played,
                'badge_count': user_profile.badges.count(),
            }
        except PlayerProfile.DoesNotExist:
            pass
    
    return Response({
        'leaderboard': leaderboard_data,
        'user_rank': user_rank,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def badges_list(request):
    """
    Mevcut tüm rozetleri ve kullanıcının kazandıklarını döndürür.
    """
    all_badges = Badge.objects.all()
    earned = []
    
    if request.user.is_authenticated:
        try:
            profile = request.user.player_profile
            earned = list(profile.badges.values_list('id', flat=True))
        except PlayerProfile.DoesNotExist:
            pass
    
    badges_data = []
    for badge in all_badges:
        badges_data.append({
            'id': badge.pk,
            'name': badge.name,
            'description': badge.description,
            'icon': badge.icon,
            'points': badge.points,
            'earned': badge.pk in earned,
        })
    
    return Response({'badges': badges_data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def earn_badge(request):
    """
    Kullanıcıya rozet kazandırır.
    Beklenen veri: {"badge_id": 1} veya {"badge_code": "first_win"}
    """
    badge_id = request.data.get('badge_id')
    badge_code = request.data.get('badge_code')
    
    try:
        if badge_id:
            badge = Badge.objects.get(id=badge_id)
        elif badge_code:
            badge = Badge.objects.get(name=badge_code)
        else:
            return Response({'error': 'badge_id veya badge_code gereklidir.'}, status=status.HTTP_400_BAD_REQUEST)
        
        profile = request.user.player_profile
        if badge in profile.badges.all():
            return Response({'message': 'Bu rozet zaten kazanılmış.'}, status=status.HTTP_200_OK)
        
        profile.award_badge(badge)
        return Response({
            'message': f'Rozet kazanıldı: {badge.name}',
            'badge': {
                'id': badge.pk,
                'name': badge.name,
                'icon': badge.icon,
                'points': badge.points,
            },
            'new_score': profile.total_score,
        })
    except Badge.DoesNotExist:
        return Response({'error': 'Rozet bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)
    except PlayerProfile.DoesNotExist:
        return Response({'error': 'Oyuncu profili bulunamadı.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_simulation_score(request):
    """
    Finansal simülasyon skorunu kaydeder.
    Beklenen veri: {"score": 1234}
    """
    score = request.data.get('score')
    if score is None:
        return Response({'error': 'Skor zorunludur.'}, status=status.HTTP_400_BAD_REQUEST)
    # Burada gerçek ortamda skor kaydedilir
    return Response({'message': f'Skor kaydedildi: {score}'}) 


@api_view(['GET'])
@permission_classes([AllowAny])
def personalize(request):
    """
    Oyun için kişiselleştirilmiş ayarları döndürür.
    Query: ?game=quiz|stock-market|budget-challenge|investment-simulator|trade-sim
    """
    game = request.query_params.get('game', 'quiz')
    settings = recommend_settings(request.user, game)
    return Response({
        'message': _('Kişiselleştirilmiş ayarlar'),
        'data': settings.to_dict(),
        'authenticated': bool(request.user and request.user.is_authenticated),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track(request):
    """
    Kullanıcı oyun etkinliği takibi.
    Body: {"game": str, "category": str, "outcome": "correct"|"incorrect"}
    """
    game = request.data.get('game') or 'quiz'
    category = request.data.get('category') or 'Eğitim'
    outcome = request.data.get('outcome')

    if outcome not in ('correct', 'incorrect'):
        return Response({'error': _('Geçersiz outcome değeri')}, status=status.HTTP_400_BAD_REQUEST)

    res = track_event(request.user, game=game, category=category, correct=(outcome == 'correct'))
    return Response({'message': _('Kayıt alındı'), 'data': res})