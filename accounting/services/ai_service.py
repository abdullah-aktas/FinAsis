from finance.accounting.models import (
    Voucher,
    VoucherLine,
    Account,
    VoucherType,
    Currency,
)
from accounting.models import Company
from decimal import Decimal
from typing import Dict
from finance.accounting.models import AutoBookingRule
from django.utils import timezone
from ..decorators import atomic_with_rollback_logging, validate_balance_before_commit
import logging

logger = logging.getLogger(__name__)


class SimpleVoucherClassifier:
    """
    Basit anahtar kelime tabanlı sınıflandırıcı: alış/satış/gider/banka.
    Yerel, hızlı ve açıklanabilir. (ML bağımlılığı olmadan kullanılır)
    """

    def predict(self, text: str) -> str:
        t = (text or "").lower()
        if any(k in t for k in ["satış", "satis", "fatura satış", "e-fatura satış"]):
            return "sales"
        if any(k in t for k in ["alış", "alis", "satın alma", "supplier", "tedarikçi"]):
            return "purchase"
        if any(k in t for k in ["gider", "fatura gider", "harcama", "expense"]):
            return "expense"
        if any(k in t for k in ["banka", "havale", "eft", "pos"]):
            return "bank"
        return "expense"


def suggest_accounting_entry(*args, **kwargs):
    return None


def analyze_financial_data(*args, **kwargs):
    return None


def map_ocr_to_voucher_lines(company: Company, ocr_data: Dict) -> Dict:
    """
    OCR verisini Tek Düzen Hesap Planı'na göre fiş satırlarına dönüştürür (basit kurallar).
    Beklenen ocr_data: { invoice_number, date, total, tax_rate, company_name }
    """
    total_str = str(ocr_data.get("total", "0")).replace(".", "").replace(",", ".")
    try:
        total = Decimal(total_str)
    except Exception:
        total = Decimal("0")
    tax_rate_str = str(ocr_data.get("tax_rate", "0")).replace(",", ".")
    try:
        tax_rate = Decimal(tax_rate_str)
    except Exception:
        tax_rate = Decimal("0")
    kdv = (
        (total * tax_rate / Decimal("100")).quantize(Decimal("0.01"))
        if tax_rate
        else Decimal("0.00")
    )
    matrah = (total - kdv).quantize(Decimal("0.01")) if total else Decimal("0.00")

    def get_account(code: str, name_fallback: str) -> Account:
        acc, _ = Account.objects.get_or_create(
            company=company, code=code, defaults={"name": name_fallback, "type_id": 1}
        )
        return acc

    # Kural tabanlı doğa belirleme (firma kuralları > basit sınıflandırıcı)
    text_blob = f"{ocr_data.get('company_name','')} {ocr_data.get('invoice_number','')}"
    rule_qs = AutoBookingRule.objects.filter(company=company, is_active=True).order_by(
        "priority"
    )
    nature = None
    selected_rule = None
    import re

    for r in rule_qs:
        try:
            if re.search(r.keyword_pattern, text_blob, re.IGNORECASE):
                nature = r.nature
                selected_rule = r
                break
        except re.error:
            # Geçersiz regex varsa atla
            continue
    if not nature:
        clf = SimpleVoucherClassifier()
        nature = clf.predict(text_blob)
    # Kuralda özel hesap kodları varsa kullan
    account_kdv = get_account(
        getattr(selected_rule, "kdv_account_code", None) or "191", "İndirilecek KDV"
    )
    account_saticilar = get_account(
        getattr(selected_rule, "credit_account_code", None) or "320", "Satıcılar"
    )
    account_alicilar = get_account(
        getattr(selected_rule, "debit_account_code", None) or "120", "Alıcılar"
    )
    account_gelir = get_account("600", "Yurtiçi Satışlar")
    account_gider = get_account("740", "Hizmet Üretim Maliyeti")

    lines = []
    if nature == "purchase" or nature == "expense":
        lines.append(
            {
                "account": account_gider,
                "description": f"{ocr_data.get('company_name','')} - {ocr_data.get('invoice_number','')}",
                "debit": matrah,
                "credit": Decimal("0.00"),
            }
        )
        if kdv > 0:
            lines.append(
                {
                    "account": account_kdv,
                    "description": "KDV",
                    "debit": kdv,
                    "credit": Decimal("0.00"),
                }
            )
        lines.append(
            {
                "account": account_saticilar,
                "description": "Satıcı borcu",
                "debit": Decimal("0.00"),
                "credit": total,
            }
        )
    elif nature == "sales":
        lines.append(
            {
                "account": account_alicilar,
                "description": f"{ocr_data.get('company_name','')} - {ocr_data.get('invoice_number','')}",
                "debit": total,
                "credit": Decimal("0.00"),
            }
        )
        if kdv > 0:
            # 391 Hesaplanmış KDV
            account_391 = get_account("391", "Hesaplanan KDV")
            lines.append(
                {
                    "account": account_391,
                    "description": "KDV",
                    "debit": Decimal("0.00"),
                    "credit": kdv,
                }
            )
        lines.append(
            {
                "account": account_gelir,
                "description": "Satış geliri",
                "debit": Decimal("0.00"),
                "credit": matrah,
            }
        )
    else:
        # varsayılan gider
        lines.append(
            {
                "account": account_gider,
                "description": f"{ocr_data.get('company_name','')} - {ocr_data.get('invoice_number','')}",
                "debit": matrah,
                "credit": Decimal("0.00"),
            }
        )
        lines.append(
            {
                "account": account_saticilar,
                "description": "Satıcı borcu",
                "debit": Decimal("0.00"),
                "credit": total,
            }
        )

    return {
        "date": ocr_data.get("date") or timezone.now().date().isoformat(),
        "reference": ocr_data.get("invoice_number"),
        "lines": lines,
        "total": total,
        "nature": nature,
        "rule_id": getattr(selected_rule, "id", None),
    }


@atomic_with_rollback_logging
@validate_balance_before_commit
def create_voucher_from_lines(company: Company, mapped: Dict) -> Voucher:
    """
    Creates a voucher from mapped lines with transaction management.
    Ensures atomicity and validates balance before commit.
    """
    from finance.enhanced_accounting_models import FiscalPeriod

    # Use FiscalPeriod instead of FiscalYear
    current_date = timezone.now().date()
    fiscal_period = FiscalPeriod.objects.filter(
        company=company, start_date__lte=current_date, end_date__gte=current_date
    ).first()

    if not fiscal_period:
        # Create a default fiscal period for current year
        fiscal_period = FiscalPeriod.objects.create(
            company=company,
            name=f"FY {timezone.now().year}",
            start_date=timezone.now().date().replace(month=1, day=1),
            end_date=timezone.now().date().replace(month=12, day=31),
            is_closed=False,
        )

    vt, _ = VoucherType.objects.get_or_create(
        code="MM", defaults={"name": "Muhasebe Fişi", "prefix": "MM"}
    )
    currency, _ = Currency.objects.get_or_create(
        code=getattr(company, "base_currency", "TRY"),
        defaults={
            "name": "Para Birimi",
            "symbol": getattr(company, "base_currency", "TRY"),
        },
    )
    number = str(Voucher.objects.filter(company=company, type=vt).count() + 1)

    voucher = Voucher.objects.create(
        company=company,
        fiscal_period=fiscal_period,
        type=vt,
        number=number,
        date=mapped["date"],
        description=f"OCR Fiş: {mapped.get('reference')}",
        reference=mapped.get("reference"),
        currency=currency,
    )

    line_no = 1
    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")

    for l in mapped["lines"]:
        VoucherLine.objects.create(
            voucher=voucher,
            line_no=line_no,
            account=l["account"],
            description=l["description"],
            debit_amount=l["debit"],
            credit_amount=l["credit"],
        )
        total_debit += l["debit"]
        total_credit += l["credit"]
        line_no += 1

    # Validate balance (is_balanced is a method, not an attribute)
    if hasattr(voucher, "is_balanced"):
        if callable(voucher.is_balanced):
            balanced = voucher.is_balanced()
        else:
            balanced = total_debit == total_credit
    else:
        balanced = total_debit == total_credit

    logger.info(
        f"Created voucher {voucher.number} for company {getattr(company, 'pk', 'unknown')}, "
        f"balanced: {balanced}"
    )

    return voucher


def map_text_to_voucher_lines(company: Company, text: str) -> Dict:
    """
    Serbest metni (chat/ses yazıya dönmüş) TDHP fiş satırlarına dönüştür.
    Basit kural tabanlı anahtar kelime çıkarımı: toplam, kdv, karşı hesap.
    """
    import re

    total_match = re.search(r"(toplam|tutar)[:\s]*([\d.,]+)", (text or "").lower())
    kdv_match = re.search(r"kdv[:\s]*%?([\d.,]+)", (text or "").lower())
    ref_match = re.search(
        r"(fatura|fis|belge)\s*no[:\s]*([a-z0-9-]+)", (text or "").lower()
    )
    total_str = total_match.group(2) if total_match else "0"
    tax_rate_str = kdv_match.group(1) if kdv_match else "0"
    reference = ref_match.group(2).upper() if ref_match else ""
    ocr_like = {
        "total": total_str,
        "tax_rate": tax_rate_str,
        "invoice_number": reference,
        "company_name": "",
    }
    mapped = map_ocr_to_voucher_lines(company, ocr_like)
    return mapped


def suggest_rules_from_samples(company: Company, samples: Dict) -> Dict:
    """
    Örnek metin/OCR girdilerinden AutoBookingRule önerir.
    Basit yaklaşımla, en sık geçen kelimeleri ve tespit edilen nature'a göre hesap kodlarını önerir.
    """
    from collections import Counter

    texts = samples.get("texts", []) + [
        f"{s.get('company_name','')} {s.get('invoice_number','')}"
        for s in samples.get("ocr", [])
    ]
    word_counter = Counter()
    clf = SimpleVoucherClassifier()
    for t in texts:
        for w in (t or "").lower().split():
            if len(w) > 3:
                word_counter[w] += 1
    common = [w for w, c in word_counter.most_common(5)]
    nature_guess = clf.predict(" ".join(common)) if common else "expense"
    # Varsayılan hesap önerileri
    default_map = {
        "purchase": {"debit": "740", "credit": "320", "kdv": "191"},
        "expense": {"debit": "770", "credit": "320", "kdv": "191"},
        "sales": {"debit": "120", "credit": "600", "kdv": "391"},
        "bank": {"debit": "102", "credit": "320", "kdv": None},
    }
    accounts = default_map.get(nature_guess, default_map["expense"])
    pattern = "|".join(common) if common else ".*"
    suggestion = {
        "name": f"Otomatik - {nature_guess}",
        "keyword_pattern": pattern,
        "nature": nature_guess,
        "debit_account_code": accounts["debit"],
        "credit_account_code": accounts["credit"],
        "kdv_account_code": accounts["kdv"],
        "priority": 100,
    }
    return {"suggestions": [suggestion]}
