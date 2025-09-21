# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone

from src.apps.accounting.models import Invoice
from src.apps.accounting.services.efatura_service import check_invoice_status, send_invoice_to_gib


class Command(BaseCommand):
    help = 'Hatalı e-Fatura gönderimlerini retry eder ve durumunu günceller'

    def handle(self, *args, **options):
        errs = Invoice.objects.filter(gib_status='error').order_by('-gib_sent_at')[:50]
        retried = 0
        for inv in errs:
            try:
                # Stateless basit retry: yeniden gönder
                send_invoice_to_gib(inv)
                retried += 1
            except Exception:
                continue
        self.stdout.write(self.style.SUCCESS(f"Retry edilen: {retried}"))


