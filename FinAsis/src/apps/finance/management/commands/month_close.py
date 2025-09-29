# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from decimal import Decimal

from src.apps.accounting.models import Company
from src.apps.finance.enhanced_accounting_models import FiscalPeriod, TrialBalanceSnapshot
from src.apps.finance.tasks import compute_monthly_depreciation

class Command(BaseCommand):
    help = 'Ay kapanışı: amortisman, mizan snapshot ve mali dönem denetimleri'

    def add_arguments(self, parser):
        parser.add_argument('--company-id', type=int, required=True, help='Şirket ID')
        parser.add_argument('--date', type=str, help='YYYY-MM-DD (varsayılan bugün)')
        parser.add_argument('--skip-depreciation', action='store_true', help='Amortismanı atla')

    def handle(self, *args, **options):
        run_date = timezone.now().date()
        if options.get('date'):
            from datetime import datetime
            run_date = datetime.strptime(options['date'], '%Y-%m-%d').date()
        company_id = options['company_id']
        try:
            company = Company.objects.get(pk=company_id)
        except Company.DoesNotExist:
            raise CommandError('Company not found')

        # İlgili mali dönem
        fiscal_period = FiscalPeriod.objects.filter(company=company, start_date__lte=run_date, end_date__gte=run_date).first()
        if not fiscal_period:
            raise CommandError('No fiscal period found for date')
        if fiscal_period.is_closed:
            self.stdout.write(self.style.WARNING('Fiscal period already closed; skipping month close logic.'))
            return

        # Amortisman
        if not options['skip_depreciation']:
            # type: ignore[attr-defined] -> Django runtime provides .id; using pk for clarity
            compute_monthly_depreciation.delay(company.pk, str(run_date))
            self.stdout.write(self.style.SUCCESS('Triggered depreciation task'))

        # Mizan snapshot
        snapshot = TrialBalanceSnapshot.build_snapshot(company, fiscal_period, as_of_date=run_date, user=None)
        self.stdout.write(self.style.SUCCESS(f'Snapshot created with {len(snapshot.account_balances)} accounts.'))

        self.stdout.write(self.style.SUCCESS('Month close base operations finished (period not marked closed yet).'))
