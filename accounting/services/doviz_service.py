from decimal import Decimal


def convert(
    amount: Decimal, from_ccy: str, to_ccy: str, rates: dict[str, float]
) -> Decimal:
    """Basit döviz çevirimi (rates dict: 1 TRY karşılığı)."""
    if from_ccy == to_ccy:
        return amount
    try:
        # amount [from] -> TRY -> [to]
        try_rate_from = Decimal(str(rates.get(from_ccy, 1.0)))
        try_rate_to = Decimal(str(rates.get(to_ccy, 1.0)))
        in_try = amount * try_rate_from
        return (in_try / try_rate_to).quantize(Decimal("0.01"))
    except Exception:
        return amount
