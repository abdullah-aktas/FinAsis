# -*- coding: utf-8 -*-
from decimal import Decimal
from dataclasses import dataclass, field
from typing import List


@dataclass
class StockLayer:
    quantity: Decimal
    unit_cost: Decimal

    @property
    def total_cost(self) -> Decimal:
        return (self.quantity * self.unit_cost).quantize(Decimal('0.01'))


@dataclass
class FifoCostResult:
    consumed_layers: List[StockLayer] = field(default_factory=list)
    cost_of_issued: Decimal = Decimal('0.00')


def fifo_consume(layers: List[StockLayer], issue_qty: Decimal) -> FifoCostResult:
    """FIFO katman tüketimi. Giriş katmanlarından sırayla tüketir ve maliyeti hesaplar."""
    result = FifoCostResult()
    remaining = Decimal(issue_qty)
    for layer in list(layers):
        if remaining <= 0:
            break
        take = min(layer.quantity, remaining)
        cost = (take * layer.unit_cost).quantize(Decimal('0.01'))
        result.cost_of_issued += cost
        result.consumed_layers.append(StockLayer(quantity=take, unit_cost=layer.unit_cost))
        layer.quantity -= take
        remaining -= take
    if remaining > 0:
        raise ValueError("Yetersiz stok katmanı")
    # Sıfırlanan katmanları temizle
    layers[:] = [l for l in layers if l.quantity > 0]
    return result


