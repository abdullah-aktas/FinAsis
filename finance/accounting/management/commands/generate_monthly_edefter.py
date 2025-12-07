# -*- coding: utf-8 -*-
r"""
Aylık e-Defter Oluşturma ve Gönderme Komutu

Kullanım:
  python manage.py generate_monthly_edefter --year 2025 --month 9 [--send]

Windows Task Scheduler ile otomasyonu:
  1. Task Scheduler'ı açın (taskschd.msc)
  2. "Create Basic Task" seçin
  3. İsim: "FinAsis Aylık e-Defter"
  4. Trigger: Monthly, ayın ilk günü
  5. Action: Start a program
     Program/script: D:\FinAsis\.venv\Scripts\python.exe
     Arguments: manage.py generate_monthly_edefter --year <yıl> --month <ay> --send
     Start in: D:\FinAsis
  6. Alternatif olarak, bir .bat dosyası oluşturup onu çalıştırın:
     edefter_monthly.bat içeriği:
       @echo off
       cd /d D:\FinAsis
       call .venv\Scripts\activate.bat
       python manage.py generate_monthly_edefter --year %date:~-4% --month %date:~-7,2% --send
       if errorlevel 1 (
         echo Hata oluştu! >> D:\FinAsis\edefter_errors.log
       )
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.accounting.models import Company, EDefter
from apps.accounting.services.edefter_service import (
    fetch_journal_dtos,
    generate_and_attach_edefter,
    send_edefter_to_gib,
)
import logging

logger = logging.getLogger("edefter")


class Command(BaseCommand):
    help = "Aylık e-Defter üretir, iliştirir ve opsiyonel olarak GİB'e gönderir"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            help="Yıl (örn: 2025). Belirtilmezse mevcut yıl kullanılır.",
        )
        parser.add_argument(
            "--month",
            type=int,
            help="Ay (1-12). Belirtilmezse mevcut ay kullanılır.",
        )
        parser.add_argument(
            "--company",
            type=int,
            help="Şirket ID'si. Belirtilmezse tüm aktif şirketler için çalıştırılır.",
        )
        parser.add_argument(
            "--send",
            action="store_true",
            help="Üretilen e-Defter'leri GİB'e gönderir.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Mevcut kayıtlar varsa üzerine yazar.",
        )

    def handle(self, *args, **options):
        now = timezone.now()
        year = options.get("year") or now.year
        month = options.get("month") or now.month

        if not (1 <= month <= 12):
            raise CommandError(f"Geçersiz ay: {month}. 1-12 arası olmalı.")

        company_id = options.get("company")
        send_to_gib = options.get("send", False)
        force = options.get("force", False)

        if company_id:
            try:
                companies = [Company.objects.get(pk=company_id, is_active=True)]
            except Company.DoesNotExist:
                raise CommandError(
                    f"Şirket bulunamadı veya aktif değil: ID={company_id}"
                )
        else:
            companies = Company.objects.filter(is_active=True)

        if not companies:
            self.stdout.write(self.style.WARNING("Aktif şirket bulunamadı."))
            return

        total_ok = 0
        total_err = 0

        for company in companies:
            try:
                self.stdout.write(f"İşleniyor: {company.name} (ID={company.pk})")

                # Fiş var mı kontrol et
                entries = fetch_journal_dtos(company, year, month)
                if not entries:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  {company.name} için {year}-{month:02d} döneminde fiş bulunamadı. Atlanıyor."
                        )
                    )
                    continue

                # EDefter kaydı var mı kontrol et
                edefter, created = EDefter.objects.get_or_create(
                    company=company,
                    year=year,
                    month=month,
                    type="yevmiye",
                    defaults={"status": "taslak"},
                )

                if not created and not force:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  {company.name} için {year}-{month:02d} e-Defter zaten mevcut (ID={edefter.pk}). --force ile üzerine yazabilirsiniz."
                        )
                    )
                    continue

                # e-Defter üret ve iliştir
                generate_and_attach_edefter(edefter, company, year, month, entries)
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ e-Defter üretildi: ID={edefter.pk}")
                )

                # GİB'e gönderim (opsiyonel)
                if send_to_gib:
                    send_edefter_to_gib(edefter)
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✓ GİB'e gönderildi: ID={edefter.pk}")
                    )

                total_ok += 1

            except Exception as e:
                logger.error(
                    f"Şirket {company.pk} için e-Defter üretiminde hata: {e}",
                    exc_info=True,
                )
                self.stdout.write(self.style.ERROR(f"  ✗ Hata: {e}"))
                total_err += 1

        # Özet
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Başarılı: {total_ok}"))
        if total_err:
            self.stdout.write(self.style.ERROR(f"Hatalı: {total_err}"))
