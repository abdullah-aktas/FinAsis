from django.apps import AppConfig


class AccountingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounting"

    def ready(self):  # type: ignore[override]
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
