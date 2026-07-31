from asyncio import TaskGroup
import asyncio
from typing import Optional

import httpx
from app.infrastructure.postgres.manager import DatabaseManager
from app.api.schemas.protection import ProtectionQuoteIn, ProtectionQuoteOut
from app.api.schemas.payment import PaymentQuoteIn
from app.infrastructure.postgres.models import Booking, EventSeat
from app.domain.enums import BookingStatus, SeatStatus
from app.domain.exceptions import EventNotFoundError, EventSeatNotFoundError, PaymentNotAvailableError, SeatReservationError
from app.api.schemas.booking import CheckoutBooking, CheckoutResponse
from datetime import UTC, datetime, timedelta
from app.config import BOOKING_TTL_MINUTES
from app.infrastructure.api_connectors.external.payment import PaymentConnector
from app.infrastructure.api_connectors.external.protection import ProtectionConnector


class BookingService:
    def __init__(
        self, 
        db_manager: DatabaseManager,
        payment_connector: PaymentConnector,
        protection_connector: ProtectionConnector
    ) -> None:
        self.db_manager = db_manager
        self.payment_connector = payment_connector
        self.protection_connector = protection_connector

    async def reservation_processing(self, event_id: int, seat_ids: list[int], user_id: int) -> CheckoutResponse: 
        try:
            if not (event := await self.db_manager.event_repo.get_event_by_id(event_id=event_id)):
                raise EventNotFoundError(event_id=event_id)
            seats = await self.db_manager.event_seat_repo.get_event_seat_for_update(event_id=event_id, seat_ids=seat_ids)
            not_founded_seat_ids = set(seat_ids) - {seat.seat_id for seat in seats}

            now = datetime.now(UTC).replace(tzinfo=None)
            reserved_until = now + timedelta(minutes=BOOKING_TTL_MINUTES)

            if len(seats) != len(seat_ids):
                raise EventSeatNotFoundError(event_id=event_id, seat_ids=not_founded_seat_ids)
            amount = sum(seat.price for seat in seats)
            booking = await self.db_manager.booking_repo.create(
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
                if seat.status != SeatStatus.available and not (seat.status == SeatStatus.reserved and seat.reserved_until < now):
                    raise SeatReservationError(event_id=seat.event_id, seat_id=seat.seat_id)
                seat.status = SeatStatus.reserved
                seat.booking_id = booking.id
                seat.reserved_until = reserved_until
            await self.db_manager.commit()
        except (EventNotFoundError, EventSeatNotFoundError):
            raise
        except SeatReservationError:
            await self.db_manager.rollback()
            raise

        payment_payload = PaymentQuoteIn(booking_id=booking.id, amount=amount)
        protection_payload = ProtectionQuoteIn(
            booking_id=booking.id,
            ticket_amount=amount,
            event_category=event.category,
            event_starts_at=event.starts_at,
        )
        try:
            async with TaskGroup() as tg:
                payment_task = tg.create_task(self.payment_connector.calculate(payload=payment_payload))
                protection_task = tg.create_task(self._safe_protection_quote(protection_payload))
        except* PaymentNotAvailableError as eg:
            await self._cancel_reservation(booking, seats)
            raise eg.exceptions[0]
        payment_quote = payment_task.result()
        protection_quote = protection_task.result()
    
        if protection_quote:
            booking.payment_commission = payment_quote.commission
            booking.protection_price = protection_quote.price
            booking.with_protection = True
            await self.db_manager.commit()
        
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

    async def _safe_protection_quote(self, protection_payload: ProtectionQuoteIn) -> Optional[ProtectionQuoteOut]:
        try:
            return await asyncio.wait_for(self.protection_connector.calculate(protection_payload), timeout=3.0)
        except (httpx.NetworkError, httpx.TimeoutException, TimeoutError):
            return None
        
    async def _cancel_reservation(self, booking: Booking, seats: list[EventSeat]) -> None:
        booking.status = BookingStatus.cancelled

        for seat in seats:
            seat.status = SeatStatus.available
            seat.reserved_until = None
            seat.booking_id = None
        await self.db_manager.session.commit()