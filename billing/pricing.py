from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Dict, Iterable, Optional

from django.conf import settings
from django.utils.translation import gettext as _

from .models import Plan, Price


def get_supported_regions() -> list[str]:
    return getattr(settings, "SUPPORTED_REGIONS", ["TR"])


def get_region_labels() -> Dict[str, str]:
    return getattr(settings, "REGION_LABELS", {})


def get_region_config(region: str) -> Dict[str, object]:
    pricing = getattr(settings, "REGIONAL_PRICING", {}) or {}
    if region in pricing:
        return pricing[region]
    default_region = getattr(settings, "DEFAULT_REGION", get_supported_regions()[0])
    return pricing.get(default_region, {})


def _to_decimal(value: object, default: Decimal = Decimal("0")) -> Decimal:
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


def _select_prices_for_period(
    plan: Plan, period: str, prices: Optional[Iterable[Price]] = None
) -> list[Price]:
    if prices is None:
        return list(plan.prices.filter(period=period, is_active=True))
    return [
        p
        for p in prices
        if getattr(p, "period", None) == period and getattr(p, "is_active", False)
    ]


def get_price_breakdown(
    plan: Plan,
    period: str,
    *,
    region: str,
    prices: Optional[Iterable[Price]] = None,
) -> Optional[Dict[str, object]]:
    """
    Returns localized pricing (tax included) for given plan/period.
    """
    region_cfg = get_region_config(region)
    currency = region_cfg.get(
        "currency", getattr(settings, "BASE_PRICING_CURRENCY", "TRY")
    )
    price_candidates = _select_prices_for_period(plan, period, prices)
    direct_price = next(
        (p for p in price_candidates if getattr(p, "currency", "").upper() == currency),
        None,
    )

    if direct_price is not None:
        amount = _to_decimal(getattr(direct_price, "amount", None))
        source = "direct"
    else:
        base_currency = getattr(settings, "BASE_PRICING_CURRENCY", "TRY")
        base_price = next(
            (
                p
                for p in price_candidates
                if getattr(p, "currency", "").upper() == base_currency
            ),
            None,
        )
        if base_price is None:
            return None
        multiplier = _to_decimal(region_cfg.get("price_multiplier", 1))
        amount = (
            _to_decimal(getattr(base_price, "amount", None)) * multiplier
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        source = "converted"

    tax_rate = Decimal("0.00")
    tax_note: Optional[str] = None
    if "vat_rate" in region_cfg:
        tax_rate = _to_decimal(region_cfg["vat_rate"])
    elif "gst_rate" in region_cfg:
        tax_rate = _to_decimal(region_cfg["gst_rate"])
    elif region_cfg.get("sales_tax"):
        scope = str(region_cfg["sales_tax"])
        tax_note = _("Satış vergisi bölgesel olarak uygulanır (%(scope)s).") % {
            "scope": scope
        }

    tax_amount = Decimal("0.00")
    if tax_rate > 0:
        tax_amount = (amount * tax_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    total = (amount + tax_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "amount": amount,
        "currency": currency,
        "tax_rate": tax_rate,
        "tax_rate_percent": (
            float((tax_rate * Decimal("100")).quantize(Decimal("0.01")))
            if tax_rate > 0
            else None
        ),
        "tax_amount": tax_amount,
        "total": total,
        "tax_note": tax_note,
        "source": source,
    }


def build_plan_card(
    plan: Plan, region: str, prices: Optional[Iterable[Price]] = None
) -> Dict[str, object]:
    month_info = get_price_breakdown(plan, "month", region=region, prices=prices)
    year_info = get_price_breakdown(plan, "year", region=region, prices=prices)

    currency = None
    if month_info:
        currency = month_info["currency"]
    elif year_info:
        currency = year_info["currency"]
    else:
        currency = getattr(settings, "BASE_PRICING_CURRENCY", "TRY")

    month_total = month_info["total"] if month_info else None
    year_total = year_info["total"] if year_info else None

    year_per_month = None
    if year_total is not None:
        year_per_month = (year_total / Decimal("12")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    discount_pct = None
    if month_total and year_total and month_total > 0:
        try:
            discount_pct = float(
                (Decimal("1") - (year_total / (month_total * Decimal("12"))))
                * Decimal("100")
            )
        except (InvalidOperation, ZeroDivisionError):
            discount_pct = None

    tax_rate_percent = None
    tax_amount = Decimal("0.00")
    tax_note = None
    if month_info and month_info.get("tax_rate_percent"):
        tax_rate_percent = month_info["tax_rate_percent"]
        tax_amount = month_info["tax_amount"]
        tax_note = month_info.get("tax_note")
    elif year_info and year_info.get("tax_rate_percent"):
        tax_rate_percent = year_info["tax_rate_percent"]
        tax_amount = year_info["tax_amount"]
        tax_note = year_info.get("tax_note")

    return {
        "month_amount": month_total,
        "year_amount": year_total,
        "year_per_month": year_per_month,
        "discount_pct": discount_pct,
        "currency": currency,
        "has_month": month_total is not None,
        "has_year": year_total is not None,
        "tax_rate_percent": tax_rate_percent,
        "tax_amount": tax_amount if tax_amount else None,
        "tax_note": tax_note,
        "month_breakdown": month_info,
        "year_breakdown": year_info,
        "popular": False,
    }


def resolve_region(request) -> str:
    supported = get_supported_regions()
    default_region = getattr(settings, "DEFAULT_REGION", supported[0])
    region_param = request.GET.get("region")
    if region_param and region_param in supported:
        request.session["billing_region"] = region_param
        return region_param
    session_region = request.session.get("billing_region")
    if session_region in supported:
        return session_region  # type: ignore[return-value]
    return default_region
