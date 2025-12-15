# -*- coding: utf-8 -*-
"""
Beta kampanyası indirim oranı için SystemSetting oluştur
"""
from django.core.management.base import BaseCommand
from common.models import SystemSetting


class Command(BaseCommand):
    help = "Beta kampanyası indirim oranı için SystemSetting oluşturur"

    def handle(self, *args, **options):
        setting, created = SystemSetting.objects.get_or_create(
            key="beta_campaign_discount_percent",
            defaults={
                "value": "20",
                "value_type": "integer",
                "description": "Beta kampanyası kalıcı indirim yüzdesi (örn: 20 = %20)",
                "category": "beta_campaign",
                "is_public": False,
                "is_editable": True,
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Beta kampanyası indirim oranı ayarı oluşturuldu: %{setting.value}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"ℹ️  Beta kampanyası indirim oranı ayarı zaten mevcut: %{setting.value}"
                )
            )
            # Mevcut değeri güncelle
            if setting.value != "20":
                setting.value = "20"
                setting.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Beta kampanyası indirim oranı güncellendi: %{setting.value}"
                    )
                )

