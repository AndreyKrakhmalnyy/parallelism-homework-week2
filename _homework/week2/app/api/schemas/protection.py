
from pydantic import BaseModel
from datetime import datetime


class ProtectionQuoteIn(BaseModel):
    booking_id: int
    ticket_amount: int
    event_category: str
    event_starts_at: datetime

class ProtectionQuoteOut(BaseModel):
    available: bool
    price: int
    covered_amount: int
    description: str | None = None