from datetime import datetime
from pydantic import BaseModel

from app.domain.enums import BookingStatus


class PaymentQuoteIn(BaseModel):
    booking_id: int
    amount: int
    currency: str = "RUB"

class PaymentQuoteOut(BaseModel):
    commission: int
    total: int
    payment_methods: list[str]
    expires_at: datetime | None = None

class PaymentCreate(BaseModel):
    payment_method: str
    with_protection: bool = False

class PaymentCompleted(BaseModel):
    booking_id: int
    status: BookingStatus
    charged_amount: int
    transaction_id: str

class PaymentPayIn(PaymentQuoteIn):
    payment_method: str

class PaymentPayOut(BaseModel):
    transaction_id: int
