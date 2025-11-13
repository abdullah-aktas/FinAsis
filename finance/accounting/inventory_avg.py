from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class AvgState:
    qty: Decimal = Decimal("0")
    avg_cost: Decimal = Decimal("0.00")


def receive(state: AvgState, qty: Decimal, unit_cost: Decimal) -> None:
    total_cost = state.qty * state.avg_cost + qty * unit_cost
    state.qty += qty
    if state.qty > 0:
        state.avg_cost = (total_cost / state.qty).quantize(Decimal("0.0001"))


def issue(state: AvgState, qty: Decimal) -> Decimal:
    if qty > state.qty:
        raise ValueError("Yetersiz stok")
    cogs = (qty * state.avg_cost).quantize(Decimal("0.01"))
    state.qty -= qty
    return cogs
