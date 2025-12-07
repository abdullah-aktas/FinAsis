# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from accounting.services.efatura_service import send_invoice_to_gib
from accounting.models import Invoice


class Command(BaseCommand):
    help = (
        "Bekleyen e-Fatura/e-Arşiv faturalarını kuyruğa alır ve gönderir (basit outbox)"
    )

    def handle(self, *args, **options):
        pending = Invoice.objects.filter(gib_status__isnull=True).order_by(
            "issue_date"
        )[:50]
        self.stdout.write(f"Gönderilecek {pending.count()} fatura bulundu.")
        sent = 0
        for inv in pending:
            try:
                send_invoice_to_gib(inv)
                sent += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Fatura {inv.pk} gönderilemedi: {e}")
                )
        self.stdout.write(self.style.SUCCESS(f"Gönderildi: {sent}"))
