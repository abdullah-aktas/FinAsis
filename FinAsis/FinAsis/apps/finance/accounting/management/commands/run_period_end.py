# -*- coding: utf-8 -*-
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone

from FinAsis.apps.finance.accounting.models import Voucher, VoucherLine, VoucherType, Account
from FinAsis.apps.accounting.models import Company


class Command(BaseCommand):
    help = 'Dönem sonu işlemleri: amortisman (stub), reeskont (stub), kur değerleme (stub) oluşturur'

    def handle(self, *args, **options):
        company = Company.objects.first()
        if not company:
            self.stdout.write(self.style.ERROR('Company bulunamadı'))
            return
        vt = VoucherType.objects.first()
        if not vt:
            self.stdout.write(self.style.ERROR('VoucherType bulunamadı'))
            return
        today = timezone.now().date()
        v = Voucher.objects.create(
            company=company,
            fiscal_year=company.fiscal_years.first() if hasattr(company, 'fiscal_years') else None,
            type=vt,
            number=f"DS-{today.strftime('%Y%m')}",
            date=today,
            description='Dönem Sonu İşlemleri (Stub)'
        )
        # Basit örnek: 770 Gider / 257 Birikmiş Amortisman
        acc_exp = Account.objects.filter(company=company, code='770').first()
        acc_dep = Account.objects.filter(company=company, code='257').first()
        if acc_exp and acc_dep:
            VoucherLine.objects.create(voucher=v, line_no=1, account=acc_exp, debit_amount=Decimal('1000.00'))
            VoucherLine.objects.create(voucher=v, line_no=2, account=acc_dep, credit_amount=Decimal('1000.00'))
        if v.is_balanced():
            v.post()
            self.stdout.write(self.style.SUCCESS('Dönem sonu fişi oluşturuldu ve onaylandı.'))
        else:
            self.stdout.write(self.style.WARNING('Dönem sonu fişi denksiz; lütfen hesapları kontrol edin.'))


