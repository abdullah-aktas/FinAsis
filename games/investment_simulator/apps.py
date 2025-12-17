from django.apps import AppConfig


class InvestmentSimulatorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "games.investment_simulator"
    verbose_name = "Yatırım Simülatörü"

    def ready(self):
        # Signal handlers'ı import et
        from . import signals  # noqa: F401
