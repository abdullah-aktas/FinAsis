from __future__ import annotations

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GamesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "games"
    verbose_name = _("Oyunlar ve Simülasyonlar")

    def ready(self) -> None:  # noqa: D401
        # Import signal definitions and routing hooks on startup if available.
        try:
            from . import routing  # noqa: F401
        except Exception:
            pass
