from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'
    label = 'common'
    verbose_name = 'Common'

    def ready(self):
        # Signal'ları kaydet
        from . import auto_role_assignment  # noqa F401
        
        # Post-migrate signal'ını kaydet
        post_migrate.connect(self.create_default_groups_handler, sender=self)

    def create_default_groups_handler(self, sender, **kwargs):
        """
        Migration sonrası gerekli grupları oluşturur
        """
        try:
            from .auto_role_assignment import create_required_groups
            created_count = create_required_groups()
            if created_count > 0:
                print(f"[COMMON] {created_count} grup oluşturuldu (post-migrate)")
        except Exception as e:
            print(f"[COMMON] Grup oluşturma hatası: {e}")
