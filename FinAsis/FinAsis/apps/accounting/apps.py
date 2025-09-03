from django.apps import AppConfig


class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'FinAsis.apps.accounting'


class AccountsConfig(AppConfig):
    name = 'FinAsis.apps.accounts'


class EducationConfig(AppConfig):
    name = 'FinAsis.apps.education'
