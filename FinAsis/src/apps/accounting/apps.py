from django.apps import AppConfig


class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.apps.accounting'


class AccountsConfig(AppConfig):
    name = 'src.apps.accounts'


class EducationConfig(AppConfig):
    name = 'src.apps.education'
