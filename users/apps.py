from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = _('Kullanıcı Yönetimi')
    
    def ready(self):
        """Uygulama hazır olduğunda çalışacak kodlar"""
        try:
            # Sinyalleri içe aktar
            import users.signals  # noqa
            
            # Celery görevlerini kaydet
            from django.conf import settings
            from celery.schedules import crontab
            
            # Periyodik görevleri ayarla
            settings.CELERY_BEAT_SCHEDULE.update({
                'cleanup-inactive-sessions': {
                    'task': 'users.tasks.cleanup_inactive_sessions',
                    'schedule': crontab(hour=0, minute=0),  # Her gün gece yarısı
                },
                'cleanup-old-notifications': {
                    'task': 'users.tasks.cleanup_old_notifications',
                    'schedule': crontab(hour=0, minute=0, day_of_week='monday'),  # Her Pazartesi
                },
                'cleanup-old-activities': {
                    'task': 'users.tasks.cleanup_old_activities',
                    'schedule': crontab(hour=0, minute=0, day_of_month='1'),  # Her ayın 1'i
                },
                'send-scheduled-notifications': {
                    'task': 'users.tasks.send_scheduled_notifications',
                    'schedule': crontab(minute='*/15'),  # Her 15 dakikada bir
                },
            })
            
            # Varsayılan kullanıcı gruplarını oluştur
            from django.contrib.auth.models import Group, Permission
            from django.contrib.contenttypes.models import ContentType
            from .models import User
            
            # Admin grubu
            admin_group, _ = Group.objects.get_or_create(name='Admin')
            admin_permissions = Permission.objects.all()
            admin_group.permissions.set(admin_permissions)
            
            # Kullanıcı grubu
            user_group, _ = Group.objects.get_or_create(name='Kullanıcı')
            user_content_type = ContentType.objects.get_for_model(User)
            user_permissions = Permission.objects.filter(
                content_type=user_content_type,
                codename__in=['view_user', 'change_user']
            )
            user_group.permissions.set(user_permissions)
            
        except Exception as e:
            # Hata durumunda logla
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Users app ready() hatası: {str(e)}") 