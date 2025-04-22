from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Kullanıcı Yönetimi'

    def ready(self):
        """
        Uygulama başlatıldığında sinyalleri yükle.
        """
        import accounts.signals 