# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone

from FinAsis.apps.accounting.models import Company
from FinAsis.apps.accounting.services.edefter_service import package_edefter


class Command(BaseCommand):
    help = 'e-Defter paketleme (XML+Berat) dosyalarını üretir (stub)'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, required=True)
        parser.add_argument('--month', type=int, required=True)

    def handle(self, *args, **options):
        year = options['year']
        month = options['month']
        company = Company.objects.first()
        if not company:
            self.stdout.write(self.style.ERROR('Company bulunamadı'))
            return
        yevmiye, berat = package_edefter(company, year, month)
        self.stdout.write(self.style.SUCCESS(f"e-Defter paket üretildi: yevmiye={len(yevmiye)}B, berat={len(berat)}B"))


