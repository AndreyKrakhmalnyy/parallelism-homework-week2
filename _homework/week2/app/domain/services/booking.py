from asyncio import TaskGroup
from app.api.schemas.protection import ProtectionQuoteIn
from app.api.schemas.payment import PaymentQuoteIn, PaymentQuoteOut
from app.infrastructure.postgres.models import Booking
from app.infrastructure.postgres.repositories.booking import BookingRepository
from app.infrastructure.api_connectors.external.protection import ProtectionConnector
from app.infrastructure.api_connectors.external.payment import PaymentConnector
from app.domain.enums import SeatStatus
from app.infrastructure.postgres.repositories.event_seat import EventSeatRepository
from app.domain.exceptions import EventNotFoundError, EventSeatNotFoundError, SeatNotAvailableError
from app.api.schemas.booking import CheckoutBooking, CheckoutResponse
from app.infrastructure.postgres.repositories.seat import SeatRepository
from app.infrastructure.postgres.repositories.event import EventRepository
from datetime import UTC, datetime, timedelta
from app.config import BOOKING_TTL_MINUTES


class BookingService:
    def __init__(
        self,
        event_repo: EventRepository,
        seat_repo: SeatRepository,
        event_seat_repo: EventSeatRepository,
        payment_connector: PaymentConnector,
        protection_connector: ProtectionConnector,
        booking_repo: BookingRepository,
    ) -> None:
        self.event_repo = event_repo
        self.seat_repo = seat_repo
        self.booking_repo = booking_repo
        self.event_seat_repo = event_seat_repo
        self.payment_connector = payment_connector
        self.protection_connector = protection_connector

    async def create(self, event_id: int, seat_ids: list[int], user_id: int) -> CheckoutResponse: 
        if not (event := await self.event_repo.get_event_by_id(event_id=event_id)):
            raise EventNotFoundError(event_id=event_id)
        seats = await self.event_seat_repo.get_event_seat_for_update(event_id=event_id, seat_ids=seat_ids)
        not_founded_seat_ids = set(seat_ids) - {seat.seat_id for seat in seats}
        reserved_until = datetime.now(UTC).replace(tzinfo=None) + timedelta(minutes=BOOKING_TTL_MINUTES)

        if len(seats) != len(seat_ids):
            raise EventSeatNotFoundError(event_id=event_id, seat_ids=not_founded_seat_ids)

        amount = sum(seat.price for seat in seats)
        booking = await self.booking_repo.create(
            Booking(
                event_id=event_id,
                user_id=user_id,
                amount=amount,
                payment_commission=0,
                with_protection=False,
                reserved_until=reserved_until,
                protection_price=None
            )
        )

        for seat in seats:
            if seat.status != SeatStatus.available:
                raise SeatNotAvailableError(event_id=seat.event_id, seat_id=seat.seat_id)
            seat.status = SeatStatus.available
            seat.booking_id = None
            seat.reserved_until = reserved_until
        payment_payload = PaymentQuoteIn(booking_id=booking.id, amount=amount)
        protection_payload = ProtectionQuoteIn(
            booking_id=booking.id,
            ticket_amount=amount,
            event_category=event.category,
            event_starts_at=event.starts_at,
        )

        async with TaskGroup() as tg:
            payment_task = tg.create_task(self.payment_connector.calculate(payload=payment_payload))
            protection_task = tg.create_task(self.protection_connector.calculate(payload=protection_payload))
        payment_quote = payment_task.result()
        protection_quote = protection_task.result()

        booking.payment_commission = payment_quote.commission
        booking.protection_price = protection_quote.price
        booking.with_protection = False
        return CheckoutResponse(
            booking=CheckoutBooking(
                id=booking.id,
                event_title=event.title,
                starts_at=event.starts_at,
                seats=[{"seat_id": seat.seat_id, "price": seat.price} for seat in seats],
                base_amount=booking.amount,
                payment_commission=booking.payment_commission,
                protection_price=booking.protection_price,
                with_protection=booking.with_protection,
                reserved_until=booking.reserved_until
            ),
            payment=payment_quote,
            protection=protection_quote
        )
