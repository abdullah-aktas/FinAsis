"""
Her kullanıcı tipi için test kullanıcıları oluşturur
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from accounts.models import UserType, UserSettings

User = get_user_model()


class Command(BaseCommand):
    help = 'Her kullanıcı tipi için test kullanıcıları oluşturur'

    def handle(self, *args, **options):
        test_users = [
            {
                'username': 'test_kobi',
                'email': 'kobi@test.com',
                'first_name': 'Test',
                'last_name': 'KOBİ',
                'user_type_code': 'kobi',
                'password': 'test123',
            },
            {
                'username': 'test_muhasebeci',
                'email': 'muhasebeci@test.com',
                'first_name': 'Test',
                'last_name': 'Muhasebeci',
                'user_type_code': 'muhasebeci',
                'password': 'test123',
            },
            {
                'username': 'test_musavir',
                'email': 'musavir@test.com',
                'first_name': 'Test',
                'last_name': 'Mali Müşavir',
                'user_type_code': 'mali_musavir',
                'password': 'test123',
            },
            {
                'username': 'test_egitimci',
                'email': 'egitimci@test.com',
                'first_name': 'Test',
                'last_name': 'Eğitimci',
                'user_type_code': 'egitimci',
                'password': 'test123',
            },
            {
                'username': 'test_ogrenci',
                'email': 'ogrenci@test.com',
                'first_name': 'Test',
                'last_name': 'Öğrenci',
                'user_type_code': 'ogrenci',
                'password': 'test123',
            },
            {
                'username': 'test_oyuncu',
                'email': 'oyuncu@test.com',
                'first_name': 'Test',
                'last_name': 'Oyuncu',
                'user_type_code': 'oyuncu',
                'password': 'test123',
            },
            {
                'username': 'test_yatirimci',
                'email': 'yatirimci@test.com',
                'first_name': 'Test',
                'last_name': 'Yatırımcı',
                'user_type_code': 'yatirimci',
                'password': 'test123',
            },
        ]

        with transaction.atomic():
            created_count = 0
            skipped_count = 0

            for user_data in test_users:
                user_type_code = user_data.pop('user_type_code')
                password = user_data.pop('password')

                # Kullanıcı zaten var mı?
                if User.objects.filter(username=user_data['username']).exists():
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'[-] Zaten var: {user_data["username"]}')
                    )
                    continue

                # UserType'ı al
                try:
                    user_type = UserType.objects.get(code=user_type_code)
                except UserType.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'[!] UserType bulunamadi: {user_type_code}')
                    )
                    continue

                # Kullanıcıyı oluştur
                user = User.objects.create_user(
                    password=password,
                    **user_data
                )
                user.user_type = user_type
                user.save()

                # UserSettings oluştur
                UserSettings.objects.get_or_create(
                    user=user,
                    defaults={
                        'email_notifications': True,
                        'dark_mode': False,
                    }
                )

                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'[+] Olusturuldu: {user.username} ({user_type.name}) - Sifre: {password}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n[OK] {created_count} kullanici olusturuldu, {skipped_count} atlandi.'
            )
        )
        self.stdout.write('\n=== GIRIS BILGILERI ===')
        self.stdout.write('Kullanici Adi: test_kobi, test_muhasebeci, test_musavir, vb.')
        self.stdout.write('Sifre: test123 (tum test kullanicilar icin)')
        self.stdout.write('======================\n')

