# -*- coding: utf-8 -*-
"""Finance Celery Tasks
Amortisman toplu hesaplama batch'i.
"""
try:
    from celery import shared_task  # type: ignore
except Exception:  # pragma: no cover - fallback stub for type checkers if celery not importable
    def shared_task(*dargs, **dkwargs):  # type: ignore
        def wrapper(func):
            return func
        return wrapper
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from django.contrib.auth import get_user_model

from .enhanced_accounting_models import (
    FixedAsset, DepreciationEntry, FiscalPeriod, JournalVoucher, JournalEntry, TrialBalanceSnapshot
)

User = get_user_model()

@shared_task(name='finance.compute_monthly_depreciation')
def compute_monthly_depreciation(company_id, run_date=None, user_id=None):
    """Belirli bir şirket için ay sonu amortisman hesapla ve yevmiye fişi oluştur.
    Idempotent: Aynı ay için tekrar çalıştırıldığında mevcut kayıtları tekrar oluşturmaz.
    """
    from accounting.models import Company  # local import to avoid circular
    if run_date is None:
        run_date = timezone.now().date()
    company: Company = Company.objects.get(pk=company_id)
    user = None
    if user_id:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            user = None

    # İlgili mali dönem
    fiscal_period = FiscalPeriod.objects.filter(company=company, start_date__lte=run_date, end_date__gte=run_date).first()
    if not fiscal_period or fiscal_period.is_closed:
        return {'status': 'skipped', 'reason': 'No open fiscal period for date.'}

    month_start = run_date.replace(day=1)
    month_end = run_date

    assets = FixedAsset.objects.filter(company=company, status='ACTIVE', depreciation_start_date__lte=month_end)
    if not assets.exists():
        return {'status': 'ok', 'created_entries': 0}

    created = 0
    with transaction.atomic():
        voucher = JournalVoucher.objects.create(
            company=company,
            voucher_number=f"DEP-{run_date.strftime('%Y%m')}",
            voucher_type='DEPRECIATION',
            date=month_end,
            fiscal_period=fiscal_period,
            description=f"{run_date.strftime('%Y-%m')} Amortisman Kayıtları"
        )
        line_no = 1
        total_debit = Decimal('0')
        total_credit = Decimal('0')
        for asset in assets:
            # Aylık amortisman (basit doğrusal)
            annual = asset.calculate_annual_depreciation()
            monthly = (annual / 12).quantize(Decimal('0.01'))
            # Aynı ay için var mı?
            exists = DepreciationEntry.objects.filter(
                fixed_asset=asset, date__gte=month_start, date__lte=month_end
            ).exists()
            if exists or monthly <= 0:
                continue
            DepreciationEntry.objects.create(
                fixed_asset=asset,
                fiscal_period=fiscal_period,
                date=month_end,
                amount=monthly,
                voucher=voucher,
                notes='Auto depreciation',
                is_automatic=True
            )
            # Muhasebe yevmiye satırları
            # Borç: Gider (Varsayım: 770 Genel Yönetim Giderleri altı amortisman gider hesabı?)
            # Kullanıcı konfigürasyonu ileride: Şimdilik asset.cost_account'ın gider eşleniği olduğunu varsaymıyoruz.
            expense_account = asset.cost_account  # Basit varsayım
            JournalEntry.objects.create(
                voucher=voucher,
                line_number=line_no,
                account=expense_account,
                description=f"{asset.asset_code} amortisman gideri",
                debit_amount=monthly,
                credit_amount=Decimal('0')
            )
            line_no += 1
            JournalEntry.objects.create(
                voucher=voucher,
                line_number=line_no,
                account=asset.accumulated_depreciation_account,
                description=f"{asset.asset_code} birikmiş amortisman",
                debit_amount=Decimal('0'),
                credit_amount=monthly
            )
            line_no += 1
            total_debit += monthly
            total_credit += monthly
            created += 1
        # Dengelenmiş mi?
        voucher.calculate_totals(save=True)
        if voucher.total_debit == voucher.total_credit and voucher.total_debit > 0:
            # Otomatik post
            try:
                voucher.post(user or None)
            except Exception:
                pass
        else:
            # Hiç kayıt yapılmadıysa fişi sil
            if created == 0:
                voucher.delete()
    return {'status': 'ok', 'created_entries': created}
