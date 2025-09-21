from django.apps import AppConfig

class TenancyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.apps.tenancy'
    verbose_name = 'Tenancy'
