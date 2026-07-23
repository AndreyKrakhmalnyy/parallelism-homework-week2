from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.api.schemas.payment import PaymentQuoteOut
from app.api.schemas.protection import ProtectionQuoteOut


class CheckoutBooking(BaseModel):
    id: int
    event_title: str
    starts_at: datetime
    seats: list[dict[str, Any]]
    base_amount: int
    payment_commission: int
    protection_price: int | None
    with_protection: bool
    reserved_until: datetime

class CheckoutResponse(BaseModel):
    booking: CheckoutBooking
    payment: PaymentQuoteOut
    protection: ProtectionQuoteOut | None

class BookingCreate(BaseModel):
    seat_ids: list[int] = Field(min_length=1)
