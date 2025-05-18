# -*- coding: utf-8 -*-
import firebase_admin
from firebase_admin import messaging, credentials
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import logging
from django.contrib.auth import get_user_model
from users.models import UserNotification
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)
User = get_user_model()

class NotificationService:
    """
    Firebase Cloud Messaging (FCM) ve veritabanı bildirim yönetim servisi
    """
    def __init__(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
                firebase_admin.initialize_app(cred)
        except Exception as e:
            logger.error(f"Firebase başlatma hatası: {str(e)}")
            raise

    def send_notification(self, user, title, message, notification_type='info', data=None):
        """
        Kullanıcıya bildirim gönder ve veritabanına kaydet
        """
        try:
            # Bildirim oluştur
            notification = UserNotification.objects.create(
                user=user,
                title=title,
                message=message,
                type=notification_type
            )

            # Kullanıcının FCM token'ı varsa Firebase üzerinden gönder
            if hasattr(user, 'profile') and user.profile.fcm_token:
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=message,
                    ),
                    data={
                        'type': notification_type,
                        'notification_id': str(notification.pk),
                        **(data or {})
                    },
                    token=user.profile.fcm_token,
                )
                
                response = messaging.send(message)
                logger.info(f"FCM bildirim gönderildi: {response}")
                
            return notification

        except Exception as e:
            logger.error(f"Bildirim gönderme hatası: {str(e)}")
            raise

    def send_bulk_notification(self, users, title, message, notification_type='info', data=None):
        """
        Birden fazla kullanıcıya toplu bildirim gönder
        """
        notifications = []
        tokens = []
        
        try:
            # Her kullanıcı için bildirim oluştur
            for user in users:
                notification = UserNotification.objects.create(
                    user=user,
                    title=title,
                    message=message,
                    type=notification_type
                )
                notifications.append(notification)
                
                # Kullanıcının FCM token'ı varsa listeye ekle
                if hasattr(user, 'profile') and user.profile.fcm_token:
                    tokens.append(user.profile.fcm_token)

            # FCM token'ı olan kullanıcılara toplu bildirim gönder
            if tokens:
                multicast_message = messaging.MulticastMessage(
                    notification=messaging.Notification(
                        title=title,
                        body=message,
                    ),
                    data={
                        'type': notification_type,
                        **(data or {})
                    },
                    tokens=tokens,
                )
                
                response = messaging.send_multicast(multicast_message)
                logger.info(f"Toplu FCM bildirim gönderildi: {response.success_count} başarılı, {response.failure_count} başarısız")

            return notifications

        except Exception as e:
            logger.error(f"Toplu bildirim gönderme hatası: {str(e)}")
            raise

    @staticmethod
    def get_notifications(user, is_read=None, limit=None):
        """
        Kullanıcının bildirimlerini getirir.
        
        Args:
            user: Bildirimleri getirilecek kullanıcı
            is_read (bool, optional): Okunma durumuna göre filtreleme
            limit (int, optional): Maksimum bildirim sayısı
            
        Returns:
            QuerySet: Bildirim listesi
        """
        try:
            notifications = UserNotification.objects.filter(user=user)
            if is_read is not None:
                notifications = notifications.filter(is_read=is_read)
            notifications = notifications.order_by('-created_at')
            if limit:
                notifications = notifications[:limit]
            return notifications
        except Exception as e:
            logger.error(f"Bildirimler getirilirken hata: {str(e)}")
            raise

    @staticmethod
    def mark_as_read(notification_pk):
        """
        Bildirimi okundu olarak işaretler.
        
        Args:
            notification_pk: Bildirim primary key
            
        Returns:
            bool: İşlem başarılı ise True
        """
        try:
            notification = UserNotification.objects.get(pk=notification_pk)
            notification.is_read = True
            notification.save()
            logger.info(f"Bildirim okundu olarak işaretlendi: {notification_pk}")
            return True
        except UserNotification.DoesNotExist:
            logger.error(f"Bildirim bulunamadı: {notification_pk}")
            return False
        except Exception as e:
            logger.error(f"Bildirim okundu işaretlenirken hata: {str(e)}")
            raise

    @staticmethod
    def mark_notifications_as_read(user):
        """
        Kullanıcının tüm okunmamış bildirimlerini okundu olarak işaretler.
        
        Args:
            user: Bildirimleri işaretlenecek kullanıcı
            
        Returns:
            int: İşaretlenen bildirim sayısı
        """
        try:
            count = UserNotification.objects.filter(
                user=user,
                is_read=False
            ).update(is_read=True)
            logger.info(f"{count} bildirim okundu olarak işaretlendi")
            return count
        except Exception as e:
            logger.error(f"Bildirimler okundu işaretlenirken hata: {str(e)}")
            raise

    @staticmethod
    def delete_notification(notification_pk):
        """
        Bildirimi siler.
        
        Args:
            notification_pk: Bildirim primary key
            
        Returns:
            bool: İşlem başarılı ise True
        """
        try:
            notification = UserNotification.objects.get(pk=notification_pk)
            notification.delete()
            logger.info(f"Bildirim silindi: {notification_pk}")
            return True
        except UserNotification.DoesNotExist:
            logger.error(f"Bildirim bulunamadı: {notification_pk}")
            return False
        except Exception as e:
            logger.error(f"Bildirim silinirken hata: {str(e)}")
            raise

    @staticmethod
    def delete_old_notifications(days=30):
        """
        Belirtilen günden eski bildirimleri sil
        
        Args:
            days (int): Silinecek bildirimlerin minimum yaşı (gün)
            
        Returns:
            int: Silinen bildirim sayısı
        """
        try:
            cutoff_date = timezone.now() - timedelta(days=days)
            count = UserNotification.objects.filter(created_at__lt=cutoff_date).delete()[0]
            logger.info(f"{count} eski bildirim silindi")
            return count
        except Exception as e:
            logger.error(f"Eski bildirimler silinirken hata: {str(e)}")
            raise

    @staticmethod
    def get_unread_count(user):
        """
        Kullanıcının okunmamış bildirim sayısını getirir.
        
        Args:
            user: Bildirimleri sayılacak kullanıcı
            
        Returns:
            int: Okunmamış bildirim sayısı
        """
        try:
            count = UserNotification.objects.filter(
                user=user,
                is_read=False
            ).count()
            return count
        except Exception as e:
            logger.error(f"Okunmamış bildirim sayısı alınırken hata: {str(e)}")
            raise 