import uuid
from datetime import datetime
from pydantic import Field
from pydantic import BaseModel


class PurchaseTicket(BaseModel):
    event_id: int
    tickets_count: int
    total_amount: int
    payment_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    paid_at: datetime = Field(default_factory=datetime.now)