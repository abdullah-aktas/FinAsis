import hashlib
from .models import ChainRecord
from typing import Iterable


def compute_sha256_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def ensure_record(reference: str, payload: str, status: str = 'pending') -> ChainRecord:
    hash_hex = compute_sha256_hex(payload)
    record, _ = ChainRecord.objects.get_or_create(
        reference=reference,
        hash_hex=hash_hex,
        defaults={
            'payload_preview': payload[:500],
            'status': status,
        }
    )
    return record


# Payload helpers (ensure stable, deterministic order and lightweight content)
def payload_for_invoice(invoice) -> str:
    return (
        f"INVOICE|{invoice.id}|{invoice.invoice_number}|{invoice.issue_date}|"
        f"{invoice.total_amount}|{invoice.customer_id}|{invoice.company_id if hasattr(invoice, 'company_id') else ''}|"
        f"{getattr(invoice, 'gib_uuid', '')}|{getattr(invoice, 'gib_status', '')}"
    )


def payload_for_voucher(voucher, lines: Iterable) -> str:
    # Using number, date, company, type and line checksums
    line_parts = []
    for ln in lines:
        line_parts.append(
            f"{ln.line_no}:{ln.account_id}:{ln.debit_amount}:{ln.credit_amount}:{ln.description or ''}"
        )
    lines_str = ';'.join(sorted(line_parts))
    return (
        f"VOUCHER|{voucher.id}|{voucher.number}|{voucher.date}|{voucher.company_id}|{voucher.type_id}|"
        f"{voucher.state}|{lines_str}"
    )


def payload_for_payment(payment) -> str:
    return (
        f"PAYMENT|{payment.id}|{payment.company_id}|{payment.customer_id}|{payment.amount}|"
        f"{payment.payment_method}|{payment.payment_date}|{payment.related_invoice_id or ''}"
    )


def payload_for_expense(expense) -> str:
    return (
        f"EXPENSE|{expense.id}|{expense.company_id}|{expense.category}|{expense.amount}|{expense.expense_date}|{int(expense.paid)}"
    )


def payload_for_banktxn(txn) -> str:
    return (
        f"BANKTXN|{txn.id}|{txn.account_id}|{txn.amount}|{txn.transaction_type}|{txn.date}"
    )


def payload_for_edefter(edefter) -> str:
    return (
        f"EDEFTER|{edefter.id}|{edefter.year}-{edefter.month}|{edefter.type}|{edefter.xml_file.name}|{edefter.berat_file.name}|{edefter.status}"
    )

