# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction

from typing import Optional
from src.apps.accounting.models import Company
from src.apps.finance.enhanced_accounting_models import FiscalPeriod, TrialBalanceSnapshot

class Command(BaseCommand):
    help = 'Yıl sonu kapanışı: mizan snapshot ve mali dönemi kapatır'

    def add_arguments(self, parser):
        parser.add_argument('--company-id', type=int, required=True)
        parser.add_argument('--period-id', type=int, help='Specific fiscal period id (opsiyonel)')

    def handle(self, *args, **options):
        company_id = options['company_id']
        try:
            company: Company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            raise CommandError('Company not found')

        fiscal_period: Optional[FiscalPeriod]
        if options.get('period_id'):
            fiscal_period = FiscalPeriod.objects.filter(company=company, pk=options['period_id']).first()
        else:
            # Son açık dönem
            fiscal_period = (FiscalPeriod.objects
                             .filter(company=company, is_closed=False)
                             .order_by('-start_date')
                             .first())
        if not fiscal_period:
            raise CommandError('No open fiscal period to close')
        assert fiscal_period is not None  # type narrowing for type checkers

        # Son snapshot
        snapshot = TrialBalanceSnapshot.build_snapshot(company, fiscal_period, as_of_date=fiscal_period.end_date)

        # Kapama
        fiscal_period.is_closed = True
        fiscal_period.closed_at = timezone.now()
        fiscal_period.save(update_fields=['is_closed', 'closed_at'])

        self.stdout.write(self.style.SUCCESS(
            f'Fiscal period {fiscal_period.pk} closed. Snapshot accounts: {len(snapshot.account_balances)}'
        ))
