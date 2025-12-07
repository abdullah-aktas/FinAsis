# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from accounting.models import Company
from accounting.services.edefter_service import package_edefter, package_edefter_zip


class Command(BaseCommand):
    help = "e-Defter paketleme: XML+Berat veya ZIP (opsiyonel imzalı) üretir"

    def add_arguments(self, parser):
        # Komut argümanları
        parser.add_argument("--year", type=int, required=True)
        parser.add_argument("--month", type=int, required=True)
        parser.add_argument("--zip", action="store_true", help="ZIP dosyası oluştur")
        parser.add_argument(
            "--signed", action="store_true", help="ZIP içine imzalı/TS çıktıları ekle"
        )
        parser.add_argument(
            "--out", type=str, help="ZIP çıktısını kaydetme yolu (örn: out.zip)"
        )

    def handle(self, *args, **options):
        year = options["year"]
        month = options["month"]
        company = Company.objects.first()
        if not company:
            self.stdout.write(self.style.ERROR("Company bulunamadı"))
            return
        if options.get("zip"):
            zip_bytes = package_edefter_zip(
                company, year, month, include_signed=options.get("signed") or False
            )
            if options.get("out"):
                path = options["out"]
                with open(path, "wb") as f:
                    f.write(zip_bytes)
                self.stdout.write(
                    self.style.SUCCESS(f"ZIP kaydedildi: {path} ({len(zip_bytes)}B)")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"ZIP üretildi: {len(zip_bytes)}B (stdout'a yazılmadı)"
                    )
                )
        else:
            yevmiye, berat = package_edefter(company, year, month)
            self.stdout.write(
                self.style.SUCCESS(
                    f"e-Defter paket üretildi: yevmiye={len(yevmiye)}B, berat={len(berat)}B"
                )
            )
