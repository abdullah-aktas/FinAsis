from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _

from notifications.models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    """
    Bildirimler için ViewSet.
    
    Bu ViewSet aşağıdaki işlemleri destekler:
    - Bildirimleri listeleme
    - Bildirim detaylarını görüntüleme
    - Bildirimleri okundu olarak işaretleme
    - Tüm bildirimleri okundu olarak işaretleme
    - Bildirimleri silme
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Kullanıcıya ait bildirimleri döndürür."""
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Yeni bildirim oluştururken mevcut kullanıcıyı atar."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Tek bir bildirimi okundu olarak işaretler."""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'Bildirim okundu olarak işaretlendi'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Tüm bildirimleri okundu olarak işaretler."""
        self.get_queryset().update(is_read=True)
        return Response({'status': 'Tüm bildirimler okundu olarak işaretlendi'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Okunmamış bildirim sayısını döndürür."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})

    @action(detail=False, methods=['post'])
    def register_device(self, request):
        """
        Mobil cihaz token'ını kaydet
        """
        device_token = request.data.get('device_token')
        if not device_token:
            return Response(
                {'error': _('device_token gerekli')},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Kullanıcı profilinde FCM token'ı güncelle
        user_profile = request.user.profile
        user_profile.fcm_token = device_token
        user_profile.save()

        return Response({
            'message': _('Cihaz başarıyla kaydedildi.')
        })

    @action(detail=False, methods=['post'])
    def unregister_device(self, request):
        """
        Mobil cihaz token'ını kaldır
        """
        user_profile = request.user.profile
        user_profile.fcm_token = ''
        user_profile.save()

        return Response({
            'message': _('Cihaz kaydı başarıyla kaldırıldı.')
        }) 