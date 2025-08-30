from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def earn_badge(request):
    """
    Kullanıcıya rozet kazandırır.
    Beklenen veri: {"badge_code": "..."}
    """
    badge_code = request.data.get('badge_code')
    if not badge_code:
        return Response({'error': 'Rozet kodu zorunludur.'}, status=status.HTTP_400_BAD_REQUEST)
    # Burada gerçek ortamda kullanıcıya rozet eklenir
    return Response({'message': f'Rozet kazanıldı: {badge_code}'})

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