from django.apps import AppConfig


class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.apps.accounting'

    def ready(self):  # type: ignore[override]
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass


class AccountsConfig(AppConfig):
    name = 'src.apps.accounts'


class EducationConfig(AppConfig):
    name = 'src.apps.education'
