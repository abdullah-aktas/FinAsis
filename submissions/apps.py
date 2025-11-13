from django.apps import AppConfig


class SubmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'submissions'
    verbose_name = 'Beyan/Defter Gönderimleri'

    def ready(self) -> None:  # noqa: D401
        # Register signal handlers
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid import-time failures in migrations/collectstatic contexts
            pass
