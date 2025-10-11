from django.apps import AppConfig


class IntegratorMockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.apps.integrator_mock'
    verbose_name = 'GİB Mock (HTTP)'