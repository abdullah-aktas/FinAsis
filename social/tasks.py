from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .models import Post, Comment, Notification, UserProfile
import logging
from PIL import Image
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import requests
from io import BytesIO
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task
def send_notification_email(post_id, notification_type, user_id):
    try:
        post = Post.objects.get(id=post_id)
        user = UserProfile.objects.get(user_id=user_id)
        
        # Bildirim ayarlarını kontrol et
        if not user.notification_settings.get('email_notifications', True):
            return
        
        subject = _('Yeni Bildirim')
        context = {
            'post': post,
            'user': user,
            'notification_type': notification_type
        }
        
        message = render_to_string('social/email/notification.html', context)
        plain_message = render_to_string('social/email/notification.txt', context)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.user.email],
            html_message=message,
            fail_silently=False
        )
        
        logger.info(f'Bildirim e-postası başarıyla gönderildi: {user.user.email}')
        
    except Exception as e:
        logger.error(f'Bildirim e-postası gönderilirken hata oluştu: {str(e)}')
        raise

@shared_task
def process_uploaded_image(image_path):
    try:
        # Resmi aç
        with default_storage.open(image_path, 'rb') as f:
            img = Image.open(f)
            
            # Resmi optimize et
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            
            # Resmi yeniden boyutlandır
            max_size = (1200, 1200)
            img.thumbnail(max_size, Image.LANCZOS)
            
            # Optimize edilmiş resmi kaydet
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            # Orijinal dosyayı sil
            default_storage.delete(image_path)
            
            # Yeni dosyayı kaydet
            new_path = image_path.replace('.png', '.jpg').replace('.gif', '.jpg')
            default_storage.save(new_path, ContentFile(output.read()))
            
            logger.info(f'Resim başarıyla işlendi: {new_path}')
            
    except Exception as e:
        logger.error(f'Resim işlenirken hata oluştu: {str(e)}')
        raise

@shared_task
def process_uploaded_video(video_path):
    try:
        # Video işleme işlemleri burada yapılacak
        # Örnek: FFmpeg ile video optimizasyonu
        pass
        
    except Exception as e:
        logger.error(f'Video işlenirken hata oluştu: {str(e)}')
        raise

@shared_task
def check_spam_content(content_id, content_type):
    try:
        if content_type == 'post':
            content = Post.objects.get(id=content_id)
        else:
            content = Comment.objects.get(id=content_id)
        
        # Spam kontrolü için içerik analizi
        spam_score = 0
        
        # URL kontrolü
        if 'http' in content.content.lower():
            spam_score += 1
        
        # E-posta kontrolü
        if '@' in content.content:
            spam_score += 1
        
        # Spam skoru yüksekse içeriği devre dışı bırak
        if spam_score >= 2:
            content.is_active = False
            content.save()
            
            # Kullanıcıya bildirim gönder
            Notification.objects.create(
                recipient=content.author,
                notification_type='spam_detected',
                content_object=content
            )
            
            logger.info(f'Spam içerik tespit edildi: {content_id}')
        
    except Exception as e:
        logger.error(f'Spam kontrolü sırasında hata oluştu: {str(e)}')
        raise

@shared_task
def send_daily_notification_summary():
    try:
        # Son 24 saatteki bildirimleri al
        notifications = Notification.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=1),
            is_read=False
        ).select_related('recipient')
        
        # Kullanıcı bazında grupla
        user_notifications = {}
        for notification in notifications:
            if notification.recipient_id not in user_notifications:
                user_notifications[notification.recipient_id] = []
            user_notifications[notification.recipient_id].append(notification)
        
        # Her kullanıcıya özet e-postası gönder
        for user_id, user_notifs in user_notifications.items():
            user = UserProfile.objects.get(user_id=user_id)
            
            if not user.notification_settings.get('daily_summary', True):
                continue
            
            subject = _('Günlük Bildirim Özeti')
            context = {
                'user': user,
                'notifications': user_notifs
            }
            
            message = render_to_string('social/email/daily_summary.html', context)
            plain_message = render_to_string('social/email/daily_summary.txt', context)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.user.email],
                html_message=message,
                fail_silently=False
            )
        
        logger.info('Günlük bildirim özetleri başarıyla gönderildi')
        
    except Exception as e:
        logger.error(f'Günlük bildirim özetleri gönderilirken hata oluştu: {str(e)}')
        raise

@shared_task
def cleanup_old_notifications():
    try:
        # 30 günden eski okunmuş bildirimleri sil
        old_notifications = Notification.objects.filter(
            is_read=True,
            created_at__lt=timezone.now() - timezone.timedelta(days=30)
        )
        
        count = old_notifications.count()
        old_notifications.delete()
        
        logger.info(f'{count} eski bildirim başarıyla silindi')
        
    except Exception as e:
        logger.error(f'Eski bildirimler silinirken hata oluştu: {str(e)}')
        raise 