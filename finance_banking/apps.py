from django.apps import AppConfig


class FinanceBankingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance_banking'
    label = 'bank_integration'  # Unique label to avoid conflict with finance.banking
    verbose_name = 'Bank Integration'

