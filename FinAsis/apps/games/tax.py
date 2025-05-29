from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class TaxRecord:
    id: str
    type: str
    amount: float
    period: str
    due_date: datetime
    status: str
    payment_date: Optional[datetime]

class TaxManager:
    def __init__(self):
        self.records: List[TaxRecord] = []

    def add_record(self, record: TaxRecord):
        self.records.append(record)

    def update_record(self, period: str, tax_type: str, amount: float):
        for record in self.records:
            if record.period == period and record.type == tax_type:
                record.amount = amount
                return True
        return False

    def get_records(self, period: Optional[str] = None):
        if period:
            return [r for r in self.records if r.period == period]
        return self.records 