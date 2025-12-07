# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from accounting.models import Company
from finance.accounting.models import PostingRule


class Command(BaseCommand):
    help = "Örnek Muhasebe Kuralları seed eder"

    def handle(self, *args, **options):
        company = Company.objects.first()
        if not company:
            self.stdout.write(self.style.ERROR("Önce bir Company kaydı oluşturun."))
            return

        examples = [
            {
                "name": "SATIS_%20",
                "document_type": "sales_invoice",
                "priority": 10,
                "definition": {
                    "condition": {"tax_rate_eq": 0.20},
                    "lines": [
                        {"side": "D", "account": "100", "formula": "gross"},
                        {"side": "C", "account": "600", "formula": "net"},
                        {"side": "C", "account": "391", "formula": "net*tax_rate"},
                    ],
                },
            },
        ]

        for ex in examples:
            obj, created = PostingRule.objects.update_or_create(
                company=company,
                name=ex["name"],
                defaults={
                    "document_type": ex["document_type"],
                    "priority": ex["priority"],
                    "definition": ex["definition"],
                    "is_active": True,
                },
            )
            self.stdout.write(
                self.style.SUCCESS(f"{obj.name} kaydedildi (created={created})")
            )
