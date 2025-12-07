from __future__ import annotations

import os
import time

from django.core.management.base import BaseCommand, CommandParser

from edoc.gib.client import GibClient
from edoc.ubltr.invoice import Invoice, Party, Line


class Command(BaseCommand):
    help = "Send N invoices to GİB (sandbox/mock) and report success rate. Uses retry and idempotency."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--count",
            type=int,
            default=50,
            help="Number of invoices to send (default: 50)",
        )
        parser.add_argument(
            "--archive", action="store_true", help="Send as e-Arşiv (archive) invoices"
        )
        parser.add_argument(
            "--mode", type=str, default=None, help="Force EDOC_GIB_MODE (stub|http)"
        )
        parser.add_argument(
            "--sleep",
            type=float,
            default=0.0,
            help="Sleep seconds between sends (optional)",
        )

    def handle(self, *args, **options):
        count: int = options["count"]
        archive: bool = bool(options["archive"])
        mode: str | None = options["mode"]
        sleep_s: float = float(options["sleep"]) or 0.0

        if mode:
            os.environ["EDOC_GIB_MODE"] = mode

        client = GibClient()

        successes = 0
        tracking_ids: list[str] = []

        for i in range(count):
            from decimal import Decimal

            inv = Invoice(
                id=f"TEST-{i+1:04d}",
                issue_date=__import__("datetime").date.today(),
                supplier=Party(name="FinAsis Test", tax_id="1111111111"),
                customer=Party(name="Sandbox Müşteri", tax_id="2222222222"),
                lines=[
                    Line(
                        description="Hizmet",
                        quantity=Decimal("1"),
                        unit_price=Decimal("100"),
                    ),
                ],
                notes=["Sandbox gönderim"],
            )
            xml_bytes = inv.to_xml_bytes()
            idem_key = f"batch-{i:03d}"
            if archive:
                res = client.send_with_retry(xml_bytes, idempotency_key=idem_key)
            else:
                res = client.send_with_retry(xml_bytes, idempotency_key=idem_key)
            tracking_ids.append(res.tracking_id)
            if res.status in ("PENDING", "ACCEPTED"):
                successes += 1
            if sleep_s:
                time.sleep(sleep_s)

        # Poll and finalize
        accepted = 0
        for tid in tracking_ids:
            st = client.poll(tid)
            if st == "ACCEPTED":
                accepted += 1

        success_rate = accepted / float(count)
        self.stdout.write(
            self.style.SUCCESS(
                f"Accepted: {accepted}/{count} ({success_rate*100:.1f}%)"
            )
        )

        if success_rate < 0.99:
            self.stderr.write(self.style.ERROR("Success rate below 99%"))
            return 1
        return 0
