# -*- coding: utf-8 -*-
"""
Muhasebe Motoru: JSON tabanlı PostingRule kullanarak belgeyi fişe çevirme
ve KDV/kur yardımcıları.
"""
from decimal import Decimal
from dataclasses import dataclass
from typing import List, Dict, Any

from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Voucher, VoucherLine, Account, PostingRule, VoucherType


@dataclass
class DocumentLineContext:
    description: str
    net_amount: Decimal
    tax_rate: Decimal
    currency: str
    cost_center: str | None = None


def resolve_account(company, account_code: str) -> Account:
    try:
        return Account.objects.get(company=company, code=account_code)
    except Account.DoesNotExist:
        raise ValidationError(f"Hesap bulunamadı: {account_code}")


def evaluate_formula(formula: str, ctx: Dict[str, Any]) -> Decimal:
    """Güvenli mini-evaluator: izin verilen anahtarlar üzerinden hesapla."""
    allowed = {
        'net': Decimal(str(ctx.get('net_amount', 0))),
        'tax_rate': Decimal(str(ctx.get('tax_rate', 0))),
        'gross': Decimal(str(ctx.get('net_amount', 0))) * (Decimal('1') + Decimal(str(ctx.get('tax_rate', 0)))),
    }
    expr = formula.replace(' ', '')
    if expr == 'net':
        return allowed['net']
    if expr == 'gross':
        return allowed['gross']
    if expr.startswith('net*'):
        factor = Decimal(expr.split('*', 1)[1])
        return allowed['net'] * factor
    if expr == 'net*tax_rate':
        return allowed['net'] * allowed['tax_rate']
    try:
        return Decimal(expr)
    except Exception:
        raise ValidationError(f"Geçersiz formül: {formula}")


def post_document(company, fiscal_year, doc_type: str, doc_number: str, doc_date, currency: str, lines: List[DocumentLineContext]) -> Voucher:
    """Belgeyi JSON kural seti ile muhasebe fişine dönüştür."""
    rules = PostingRule.objects.filter(company=company, document_type=doc_type, is_active=True).order_by('priority')
    if not rules.exists():
        raise ValidationError("Uygun muhasebe kuralı bulunamadı.")

    vtype = VoucherType.objects.first()
    if not vtype:
        raise ValidationError("Fiş tipi tanımlı değil.")

    with transaction.atomic():
        voucher = Voucher.objects.create(
            company=company,
            fiscal_year=fiscal_year,
            type=vtype,
            number=doc_number,
            date=doc_date,
            description=f"AutoPost {doc_type} {doc_number}",
            state='draft'
        )
        line_no = 1
        for src in lines:
            ctx_dict = {
                'description': src.description,
                'net_amount': src.net_amount,
                'tax_rate': src.tax_rate,
                'currency': src.currency,
            }
            for rule in rules:
                definition = rule.definition or {}
                cond = definition.get('condition', {})
                tax_eq = cond.get('tax_rate_eq')
                if tax_eq is not None and Decimal(str(tax_eq)) != src.tax_rate:
                    continue
                for out in definition.get('lines', []):
                    side = out.get('side')
                    account_code = out.get('account')
                    formula = out.get('formula', 'net')
                    amount = evaluate_formula(formula, ctx_dict)
                    account = resolve_account(company, account_code)
                    VoucherLine.objects.create(
                        voucher=voucher,
                        line_no=line_no,
                        account=account,
                        description=src.description,
                        debit_amount=amount if side == 'D' else Decimal('0'),
                        credit_amount=amount if side == 'C' else Decimal('0'),
                    )
                    line_no += 1

        if not voucher.is_balanced():
            raise ValidationError("Fiş denksiz.")
        voucher.post()
        return voucher


def compute_tax_split(net: Decimal, rate: Decimal) -> Dict[str, Decimal]:
    tax = (net * rate).quantize(Decimal('0.01'))
    gross = net + tax
    return {"net": net, "tax": tax, "gross": gross}


def fx_value(amount: Decimal, rate: Decimal) -> Decimal:
    return (amount * rate).quantize(Decimal('0.01'))


