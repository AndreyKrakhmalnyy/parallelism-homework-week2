from enum import StrEnum


class SeatStatus(StrEnum):
    available = "available"
    reserved = "reserved"
    sold = "sold"


class BookingStatus(StrEnum):
    pending_payment = "pending_payment"
    paid = "paid"
    cancelled = "cancelled"
    expired = "expired"