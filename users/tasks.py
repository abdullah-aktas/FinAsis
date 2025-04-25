from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import UserNotification, UserActivity, UserSession
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

@shared_task
def send_welcome_email(user_id):
    """Hoş geldin e-postası gönder"""
    try:
        user = User.objects.get(id=user_id)
        subject = _('Hoş Geldiniz - {}').format(settings.SITE_NAME)
        message = render_to_string('users/email/welcome.html', {
            'user': user,
            'site_name': settings.SITE_NAME,
            'site_url': settings.SITE_URL,
        })
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )
        # Aktivite kaydı oluştur
        UserActivity.objects.create(
            user=user,
            action='welcome_email_sent',
            details='Hoş geldin e-postası gönderildi'
        )
    except User.DoesNotExist:
        pass

@shared_task
def send_verification_email(user_id):
    """E-posta doğrulama bağlantısı gönder"""
    try:
        user = User.objects.get(id=user_id)
        subject = _('E-posta Adresinizi Doğrulayın - {}').format(settings.SITE_NAME)
        verification_url = f"{settings.SITE_URL}/verify-email/{user.verification_token}/"
        message = render_to_string('users/email/verify.html', {
            'user': user,
            'verification_url': verification_url,
            'site_name': settings.SITE_NAME,
        })
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )
        # Aktivite kaydı oluştur
        UserActivity.objects.create(
            user=user,
            action='verification_email_sent',
            details='Doğrulama e-postası gönderildi'
        )
    except User.DoesNotExist:
        pass

@shared_task
def send_password_reset_email(user_id):
    """Şifre sıfırlama bağlantısı gönder"""
    try:
        user = User.objects.get(id=user_id)
        subject = _('Şifre Sıfırlama - {}').format(settings.SITE_NAME)
        reset_url = f"{settings.SITE_URL}/reset-password/{user.reset_token}/"
        message = render_to_string('users/email/password_reset.html', {
            'user': user,
            'reset_url': reset_url,
            'site_name': settings.SITE_NAME,
        })
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )
        # Aktivite kaydı oluştur
        UserActivity.objects.create(
            user=user,
            action='password_reset_email_sent',
            details='Şifre sıfırlama e-postası gönderildi'
        )
    except User.DoesNotExist:
        pass

@shared_task
def send_profile_update_notification(user_id):
    """Profil güncelleme bildirimi gönder"""
    try:
        user = User.objects.get(id=user_id)
        # Web bildirimi oluştur
        UserNotification.objects.create(
            user=user,
            title=_('Profil Güncellendi'),
            message=_('Profil bilgileriniz başarıyla güncellendi.'),
            type='info'
        )
        # E-posta bildirimi gönder
        if user.preferences.email_notifications:
            subject = _('Profil Güncellendi - {}').format(settings.SITE_NAME)
            message = render_to_string('users/email/profile_updated.html', {
                'user': user,
                'site_name': settings.SITE_NAME,
            })
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=message,
                fail_silently=False,
            )
    except User.DoesNotExist:
        pass

@shared_task
def cleanup_inactive_sessions():
    """Aktif olmayan oturumları temizle"""
    inactive_threshold = timezone.now() - timezone.timedelta(days=7)
    inactive_sessions = UserSession.objects.filter(
        last_activity__lt=inactive_threshold
    )
    inactive_sessions.delete()

@shared_task
def cleanup_old_notifications():
    """Eski bildirimleri temizle"""
    old_threshold = timezone.now() - timezone.timedelta(days=30)
    old_notifications = UserNotification.objects.filter(
        created_at__lt=old_threshold,
        is_read=True
    )
    old_notifications.delete()

@shared_task
def cleanup_old_activities():
    """Eski aktivite kayıtlarını temizle"""
    old_threshold = timezone.now() - timezone.timedelta(days=90)
    old_activities = UserActivity.objects.filter(
        created_at__lt=old_threshold
    )
    old_activities.delete()

@shared_task
def send_scheduled_notifications():
    """Zamanlanmış bildirimleri gönder"""
    now = timezone.now()
    scheduled_notifications = UserNotification.objects.filter(
        scheduled_time__lte=now,
        is_sent=False
    )
    for notification in scheduled_notifications:
        # Web bildirimi gönder
        notification.is_sent = True
        notification.save()
        # E-posta bildirimi gönder
        if notification.user.preferences.email_notifications:
            subject = notification.title
            message = render_to_string('users/email/notification.html', {
                'notification': notification,
                'site_name': settings.SITE_NAME,
            })
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                html_message=message,
                fail_silently=False,
            )

@shared_task
def update_user_activity():
    """Kullanıcı aktivitelerini günceller"""
    # Son 30 dakika içinde aktif olan kullanıcıları işaretle
    threshold = timezone.now() - timedelta(minutes=30)
    UserActivity.objects.filter(
        last_activity__lt=threshold,
        is_active=True
    ).update(is_active=False)

@shared_task
def cleanup_old_sessions():
    """Eski oturumları temizler"""
    # 30 günden eski oturumları sil
    threshold = timezone.now() - timedelta(days=30)
    UserSession.objects.filter(
        last_activity__lt=threshold
    ).delete() 