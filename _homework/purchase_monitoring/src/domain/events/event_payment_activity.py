from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass(frozen=True, slots=True, kw_only=True)
class EventPaymentActivity:
    batch_id: uuid.UUID = field(default_factory=uuid.uuid4)
    event_id: int
    payments_count: int
    tickets_count: int
    total_amount: int
    created_at: datetime = field(default_factory=datetime.now)
