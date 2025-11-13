"""
FinAsis için kullanıcı tiplerini oluşturan management command
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import UserType


class Command(BaseCommand):
    help = 'FinAsis için tüm kullanıcı tiplerini oluşturur'

    def handle(self, *args, **options):
        user_types = [
            {
                'code': 'kobi',
                'name': 'KOBİ Sahibi',
            },
            {
                'code': 'muhasebeci',
                'name': 'Muhasebeci',
            },
            {
                'code': 'mali_musavir',
                'name': 'Mali Müşavir',
            },
            {
                'code': 'egitimci',
                'name': 'Eğitimci',
            },
            {
                'code': 'ogrenci',
                'name': 'Öğrenci',
            },
            {
                'code': 'oyuncu',
                'name': 'Oyuncu',
            },
            {
                'code': 'yatirimci',
                'name': 'Yatırımcı',
            },
        ]

        with transaction.atomic():
            created_count = 0
            updated_count = 0
            
            for user_type_data in user_types:
                user_type, created = UserType.objects.update_or_create(
                    code=user_type_data['code'],
                    defaults={'name': user_type_data['name']}
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'[+] Olusturuldu: {user_type.name} ({user_type.code})')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'[*] Guncellendi: {user_type.name} ({user_type.code})')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n[OK] Tamamlandi! {created_count} yeni, {updated_count} mevcut kullanici tipi.'
            )
        )

