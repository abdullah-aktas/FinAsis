from __future__ import annotations

from typing import Literal
from django.db import transaction

from .models import Check, Bill, CheckStatus


def transition_check(check: Check, action: Literal["endorse", "deposit", "cash", "dishonor"]) -> None:
    with transaction.atomic():
        if action == "endorse":
            check.mark_as_endorsed()
        elif action == "deposit":
            check.mark_as_deposited()
        elif action == "cash":
            check.mark_as_cashed()
        elif action == "dishonor":
            check.mark_as_dishonored()
        else:
            raise ValueError("Unknown action")


def transition_bill(bill: Bill, action: Literal["endorse", "cash", "dishonor"]) -> None:
    with transaction.atomic():
        if action == "endorse":
            bill.status = CheckStatus.ENDORSED
        elif action == "cash":
            bill.status = CheckStatus.CASHED
        elif action == "dishonor":
            bill.status = CheckStatus.DISHONORED
        else:
            raise ValueError("Unknown action")
        bill.save(update_fields=["status"])


def propose_voucher_for_check(check: Check) -> dict:
    """Return a minimal voucher proposal dict (stub)."""
    direction = "incoming" if check.is_incoming else "outgoing"
    return {
        "description": f"Check {direction} {check.check_number}",
        "lines": [
            {"side": "D" if check.is_incoming else "C", "amount": check.amount, "account": check.accounting_account.code},
        ],
    }
