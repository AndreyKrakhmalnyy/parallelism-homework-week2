from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass(frozen=True, slots=True, kw_only=True)
class PaymentTicketDTO:
    event_id: int
    tickets_count: int
    total_amount: int
    payment_id: uuid.UUID = field(default_factory=uuid.uuid4)
    paid_at: datetime = field(default_factory=datetime.now)