from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BackupsConfig(AppConfig):
    name = 'backups'
    verbose_name = _('Yedekleme Sistemi')

    def ready(self):
        """
        Uygulama hazır olduğunda çalışır.
        """
        import backups.signals  # Sinyalleri kaydet
        from .tasks import cleanup_old_backups
        from django_celery_beat.models import PeriodicTask, IntervalSchedule
        import json

        # Otomatik temizleme görevi oluştur
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=24,
            period=IntervalSchedule.HOURS,
        )

        PeriodicTask.objects.get_or_create(
            interval=schedule,
            name='Temizleme Görevi',
            task='backups.tasks.cleanup_old_backups',
            defaults={
                'enabled': True,
                'description': 'Eski yedekleri temizler',
                'args': json.dumps([]),
                'kwargs': json.dumps({}),
            }
        ) 