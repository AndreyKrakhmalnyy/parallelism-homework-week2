from app.infrastructure.taskiq.tasks.cpu import generate_event_dashboard_report
from app.infrastructure.taskiq.tasks.io import sync_protection_price
from app.infrastructure.taskiq.tasks.periodic import (
    cancel_expired_bookings,
    generate_payment_ticket_events,
)

__all__ = [
    "generate_event_dashboard_report",
    "sync_protection_price",
    "cancel_expired_bookings",
    "generate_payment_ticket_events",
]