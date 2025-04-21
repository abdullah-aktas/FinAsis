import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Eğer yoksa superuser oluşturur'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@finasis.com.tr')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stdout.write(self.style.WARNING('DJANGO_SUPERUSER_PASSWORD çevre değişkeni bulunamadı, varsayılan şifre kullanılıyor'))
            password = 'admin123!'  # Varsayılan şifre

        if not User.objects.filter(username=username).exists():
            self.stdout.write(f'Superuser oluşturuluyor: {username}')
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser başarıyla oluşturuldu: {username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser zaten mevcut: {username}')) 