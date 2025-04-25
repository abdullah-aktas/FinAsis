from django.apps import AppConfig

class PermissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'permissions'
    verbose_name = 'Yetkilendirme'

    def ready(self):
        import permissions.signals  # noqa 