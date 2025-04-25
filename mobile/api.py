from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import logging
from datetime import datetime, timedelta
import json
from cryptography.fernet import Fernet
import base64
from django.core.exceptions import ValidationError
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.decorators import permission_classes, throttle_classes
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class User(AbstractUser):
    """Özelleştirilmiş kullanıcı modeli"""
    pass

class UserProfile(models.Model):
    """Kullanıcı profili modeli"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    two_factor_enabled = models.BooleanField(default=False)
    last_device_id = models.CharField(max_length=255, null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    device_info = models.JSONField(default=dict)

class Notification(models.Model):
    """Bildirim modeli"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

class MobileAPIThrottle(UserRateThrottle):
    """Mobil API için hız sınırlayıcı"""
    rate = '100/minute'  # Dakikada 100 istek

class MobileAuthAPI(APIView):
    """Mobil kimlik doğrulama API'si"""
    
    throttle_classes = [AnonRateThrottle]
    
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            device_id = request.data.get('device_id')
            device_info = request.data.get('device_info', {})
            
            if not all([username, password, device_id]):
                return Response({
                    'status': 'error',
                    'message': _('Eksik bilgi'),
                    'required_fields': ['username', 'password', 'device_id']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = authenticate(username=username, password=password)
            
            if not user:
                logger.warning(f"Başarısız giriş denemesi: {username}")
                return Response({
                    'status': 'error',
                    'message': _('Geçersiz kullanıcı adı veya şifre')
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_active:
                return Response({
                    'status': 'error',
                    'message': _('Hesap aktif değil')
                }, status=status.HTTP_403_FORBIDDEN)
            
            # İki faktörlü doğrulama kontrolü
            if user.profile.two_factor_enabled:
                two_factor_data = {
                    'user_id': user.id,
                    'device_id': device_id,
                    'device_info': device_info,
                    'timestamp': timezone.now().isoformat()
                }
                
                cache_key = f'two_factor_{user.id}_{device_id}'
                cache.set(cache_key, two_factor_data, 300)  # 5 dakika
                
                return Response({
                    'status': 'two_factor_required',
                    'message': _('İki faktörlü doğrulama gerekli'),
                    'expires_in': 300
                })
            
            # Token oluştur
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            
            # Cihaz bilgilerini kaydet
            user.profile.last_device_id = device_id
            user.profile.last_login = timezone.now()
            user.profile.device_info = device_info
            user.profile.save()
            
            # Kullanıcı aktivitesini kaydet
            self._log_user_activity(user, device_id, device_info, True)
            
            return Response({
                'status': 'success',
                'access_token': access_token,
                'refresh_token': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.get_full_name(),
                    'permissions': self._get_user_permissions(user)
                }
            })
            
        except Exception as e:
            logger.error(f"Mobil giriş hatası: {str(e)}")
            return Response({
                'status': 'error',
                'message': _('Bir hata oluştu')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _log_user_activity(self, user, device_id, device_info, success):
        """Kullanıcı aktivitesini kaydet"""
        from permissions.models import AuditLog
        
        AuditLog.objects.create(
            user=user,
            action='login',
            details={
                'device_id': device_id,
                'device_info': device_info,
                'success': success,
                'ip_address': self.request.META.get('REMOTE_ADDR'),
                'user_agent': self.request.META.get('HTTP_USER_AGENT')
            }
        )
    
    def _get_user_permissions(self, user):
        """Kullanıcı izinlerini getir"""
        permissions = []
        for perm in user.user_permissions.all():
            permissions.append(f"{perm.content_type.app_label}.{perm.codename}")
        return permissions

@permission_classes([IsAuthenticated])
@throttle_classes([MobileAPIThrottle])
class MobileTwoFactorAPI(APIView):
    """İki faktörlü doğrulama API'si"""
    
    def post(self, request):
        try:
            user = request.user
            device_id = request.data.get('device_id')
            verification_code = request.data.get('verification_code')
            
            if not all([device_id, verification_code]):
                return Response({
                    'status': 'error',
                    'message': _('Eksik bilgi'),
                    'required_fields': ['device_id', 'verification_code']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            cache_key = f'two_factor_{user.id}_{device_id}'
            two_factor_data = cache.get(cache_key)
            
            if not two_factor_data:
                return Response({
                    'status': 'error',
                    'message': _('Geçersiz veya süresi dolmuş doğrulama isteği')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Doğrulama kodunu kontrol et
            if verification_code == user.profile.two_factor_secret:
                # Token oluştur
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                
                # Cache'i temizle
                cache.delete(cache_key)
                
                # Cihaz bilgilerini güncelle
                user.profile.last_device_id = device_id
                user.profile.last_login = timezone.now()
                user.profile.device_info = two_factor_data.get('device_info', {})
                user.profile.save()
                
                return Response({
                    'status': 'success',
                    'access_token': access_token,
                    'refresh_token': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.get_full_name(),
                        'permissions': self._get_user_permissions(user)
                    }
                })
            
            return Response({
                'status': 'error',
                'message': _('Geçersiz doğrulama kodu')
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        except Exception as e:
            logger.error(f"İki faktörlü doğrulama hatası: {str(e)}")
            return Response({
                'status': 'error',
                'message': _('Bir hata oluştu')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_user_permissions(self, user):
        """Kullanıcı izinlerini getir"""
        permissions = []
        for perm in user.user_permissions.all():
            permissions.append(f"{perm.content_type.app_label}.{perm.codename}")
        return permissions

@permission_classes([IsAuthenticated])
@throttle_classes([MobileAPIThrottle])
class MobileSyncAPI(APIView):
    """Mobil veri senkronizasyonu API'si"""
    
    def post(self, request):
        try:
            user = request.user
            device_id = request.data.get('device_id')
            sync_data = request.data.get('data')
            sync_type = request.data.get('type', 'full')  # full veya partial
            
            if not all([device_id, sync_data]):
                return Response({
                    'status': 'error',
                    'message': _('Eksik bilgi'),
                    'required_fields': ['device_id', 'data']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Veri şifreleme
            encryption_key = settings.ENCRYPTION_KEY.encode()
            cipher_suite = Fernet(encryption_key)
            
            # Veriyi JSON formatına çevir ve şifrele
            encrypted_data = cipher_suite.encrypt(json.dumps(sync_data).encode())
            
            # Cache'e kaydet
            cache_key = f'sync_{user.id}_{device_id}'
            cache.set(cache_key, {
                'data': encrypted_data,
                'type': sync_type,
                'timestamp': timezone.now().isoformat()
            }, 3600)  # 1 saat
            
            return Response({
                'status': 'success',
                'message': _('Veri senkronize edildi'),
                'sync_type': sync_type,
                'timestamp': timezone.now().isoformat()
            })
            
        except ValidationError as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Veri senkronizasyon hatası: {str(e)}")
            return Response({
                'status': 'error',
                'message': _('Bir hata oluştu')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        try:
            user = request.user
            device_id = request.query_params.get('device_id')
            sync_type = request.query_params.get('type', 'full')
            
            if not device_id:
                return Response({
                    'status': 'error',
                    'message': _('Device ID gerekli')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            cache_key = f'sync_{user.id}_{device_id}'
            cached_data = cache.get(cache_key)
            
            if not cached_data:
                return Response({
                    'status': 'error',
                    'message': _('Senkronize edilmiş veri bulunamadı')
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Veri şifre çözme
            encryption_key = settings.ENCRYPTION_KEY.encode()
            cipher_suite = Fernet(encryption_key)
            
            decrypted_data = cipher_suite.decrypt(cached_data['data'])
            sync_data = json.loads(decrypted_data)
            
            return Response({
                'status': 'success',
                'data': sync_data,
                'sync_type': cached_data['type'],
                'timestamp': cached_data['timestamp']
            })
            
        except Exception as e:
            logger.error(f"Veri senkronizasyon durumu kontrol hatası: {str(e)}")
            return Response({
                'status': 'error',
                'message': _('Bir hata oluştu')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@permission_classes([IsAuthenticated])
@throttle_classes([MobileAPIThrottle])
class MobileNotificationAPI(APIView):
    """Mobil bildirim API'si"""
    
    def post(self, request):
        try:
            user = request.user
            device_id = request.data.get('device_id')
            notification_data = request.data.get('data')
            notification_type = request.data.get('type', 'info')
            
            if not all([device_id, notification_data]):
                return Response({
                    'status': 'error',
                    'message': _('Eksik bilgi'),
                    'required_fields': ['device_id', 'data']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # FCM token kontrolü
            fcm_token = user.profile.fcm_token
            if not fcm_token:
                return Response({
                    'status': 'error',
                    'message': _('FCM token bulunamadı')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Bildirimi veritabanına kaydet
            from notifications.models import Notification
            
            notification = Notification.objects.create(
                user=user,
                title=notification_data.get('title'),
                message=notification_data.get('message'),
                type=notification_type,
                data=notification_data.get('extra_data', {}),
                device_id=device_id
            )
            
            # Firebase Cloud Messaging ile bildirimi gönder
            from .utils import send_fcm_notification
            
            success = send_fcm_notification(
                fcm_token=fcm_token,
                title=notification_data.get('title'),
                message=notification_data.get('message'),
                data=notification_data.get('extra_data', {})
            )
            
            if success:
                return Response({
                    'status': 'success',
                    'message': _('Bildirim gönderildi'),
                    'notification_id': notification.id
                })
            else:
                return Response({
                    'status': 'error',
                    'message': _('Bildirim gönderilemedi')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Bildirim gönderme hatası: {str(e)}")
            return Response({
                'status': 'error',
                'message': _('Bir hata oluştu')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Bildirimleri listele"""
        try:
            user = request.user
            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 20))
            notification_type = request.query_params.get('type')
            is_read = request.query_params.get('is_read')
            
            from notifications.models import Notification
            
            # Bildirimleri filtrele
            notifications = Notification.objects.filter(user=user)
            
            if notification_type:
                notifications = notifications.filter(type=notification_type)
            
            if is_read is not None:
                notifications = notifications.filter(is_read=is_read == 'true')
            
            # Sayfalama
            start = (page - 1) * per_page
            end = start + per_page
            
            notifications = notifications.order_by('-created_at')[start:end]
            
            return Response({
                'status': 'success',
                'notifications': [{
                    'id': n.id,
                    'title': n.title,
                    'message': n.message,
                    'type': n.type,
                    'is_read': n.is_read,
                    'created_at': n.created_at.isoformat(),
                    'data': n.data
                } for n in notifications]
            })
            
        except Exception as e:
            logger.error(f"Bildirim listeleme hatası: {str(e)}")
            return Response({
                'status': 'error',
                'message': _('Bir hata oluştu')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 