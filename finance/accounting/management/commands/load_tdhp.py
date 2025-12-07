# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.translation import gettext as _
import csv
from pathlib import Path

from accounting.models import Company
from finance.accounting.models import Account, AccountType


class Command(BaseCommand):
    help = "Load TDHP (Tek Düzen Hesap Planı) accounts from a CSV file for a company."

    def add_arguments(self, parser):
        parser.add_argument(
            "--company-id", type=int, required=True, help="Target company ID"
        )
        parser.add_argument(
            "--csv",
            type=str,
            default="",
            help="Path to CSV (code,name,type_code). If omitted, uses bundled data/tdhp.csv",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Enable strict TDHP code validation during load",
        )

    def handle(self, *args, **options):
        company_id = options["company_id"]
        csv_path = options["csv"]
        strict = options["strict"]

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise CommandError(_("Company not found: %s") % company_id)

        if not csv_path:
            csv_path = (
                Path(__file__).resolve().parent.parent.parent / "data" / "tdhp.csv"
            )
        else:
            csv_path = Path(csv_path)
        if not csv_path.exists():
            raise CommandError(_("CSV file not found: %s") % str(csv_path))

        self.stdout.write(self.style.NOTICE(_("Loading TDHP from: %s") % str(csv_path)))
        created, updated = 0, 0

        @transaction.atomic
        def _load():
            nonlocal created, updated
            with csv_path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    code = (row.get("code") or "").strip()
                    name = (row.get("name") or "").strip()
                    type_code = (row.get("type_code") or "GEN").strip()

                    if not code or not name:
                        continue

                    atype, _ = AccountType.objects.get_or_create(
                        code=type_code, defaults={"name": type_code}
                    )
                    parent_code = None
                    if "." in code:
                        parent_code = code.rsplit(".", 1)[0]
                    elif "-" in code:
                        parent_code = code.rsplit("-", 1)[0]

                    parent = None
                    if parent_code:
                        parent, _ = Account.objects.get_or_create(
                            company=company,
                            code=parent_code,
                            defaults={
                                "name": parent_code,
                                "type": atype,
                            },
                        )

                    obj, is_created = Account.objects.update_or_create(
                        company=company,
                        code=code,
                        defaults={"name": name, "type": atype, "parent": parent},
                    )
                    created += int(is_created)
                    updated += int(not is_created)

        # Temporarily override strict setting if needed
        from django.conf import settings as dj_settings

        original_strict = getattr(dj_settings, "ACCOUNT_CODE_TDHP_STRICT", False)
        if strict:
            setattr(dj_settings, "ACCOUNT_CODE_TDHP_STRICT", True)
        try:
            _load()
        finally:
            setattr(dj_settings, "ACCOUNT_CODE_TDHP_STRICT", original_strict)

        self.stdout.write(
            self.style.SUCCESS(_("Done. Created: %d, Updated: %d") % (created, updated))
        )
