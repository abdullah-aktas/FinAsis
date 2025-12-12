"""
Management command: Gruplara izinleri otomatik atar
Kullanım: python manage.py assign_group_permissions [--force]
"""

from django.core.management.base import BaseCommand
from common.auto_role_assignment import (
    assign_permissions_to_all_groups,
    assign_permissions_to_group,
)
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Gruplara izinleri otomatik atar"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Mevcut izinleri temizleyip yeniden ata",
        )
        parser.add_argument(
            "--group",
            type=str,
            help="Belirli bir gruba izin ata (grup adı)",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)
        group_name = options.get("group")

        if group_name:
            # Belirli bir gruba izin ata
            try:
                group = Group.objects.get(name=group_name)
                result = assign_permissions_to_group(group, force=force)
                if result["success"]:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Grup '{group_name}' için {result.get('added', 0)} izin atandı"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ Grup '{group_name}' için izin atama hatası: {result.get('error')}"
                        )
                    )
            except Group.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"❌ Grup bulunamadı: {group_name}")
                )
        else:
            # Tüm gruplara izin ata
            result = assign_permissions_to_all_groups(force=force)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Toplam {result['total']} grup işlendi - "
                    f"Başarılı: {result['success']}, Hata: {result['errors']}"
                )
            )

            # Detaylı sonuçlar
            for res in result["results"]:
                if res["success"]:
                    self.stdout.write(
                        f"  ✓ {res['group_name']}: {res.get('added', 0)} izin"
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ✗ {res['group_name']}: {res.get('error', 'Bilinmeyen hata')}"
                        )
                    )

