from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional


@dataclass
class InventoryItem:
    id: str
    name: str
    quantity: int
    unit_cost: float
    total_cost: float
    category: str
    last_updated: datetime


class InventoryManager:
    def __init__(self):
        self.items: Dict[str, InventoryItem] = {}

    def add_item(self, item: InventoryItem):
        self.items[item.id] = item

    def update_item(self, item_id: str, quantity: int, unit_cost: float) -> bool:
        if item_id in self.items:
            item = self.items[item_id]
            item.quantity = quantity
            item.unit_cost = unit_cost
            item.total_cost = quantity * unit_cost
            item.last_updated = datetime.now()
            return True
        return False

    def get_item(self, item_id: str) -> Optional[InventoryItem]:
        return self.items.get(item_id)

    def all_items(self):
        return list(self.items.values())
