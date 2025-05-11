from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .oyunlastirma import Gamification

gamification_instance = Gamification()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_task(request):
    """
    Kullanıcıdan gelen görevi tamamlar ve ödül döner.
    """
    try:
        data = request.data
        task = data.get('task')
        if not task:
            return Response({'error': 'Görev adı boş olamaz.'}, status=status.HTTP_400_BAD_REQUEST)
        reward = gamification_instance.complete_task(task)
        if reward:
            return Response({'reward': reward}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Geçersiz veya daha önce tamamlanmış görev.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 