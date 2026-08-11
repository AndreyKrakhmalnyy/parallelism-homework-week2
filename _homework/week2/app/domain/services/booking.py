import asyncio

import httpx
from app.infrastructure.taskiq.tasks import get_protection_price
from app.infrastructure.postgres.manager import DatabaseManager
from app.api.schemas.protection import ProtectionQuoteIn
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
        """Резервирует места и считает итоговую стоимость чекаута.

        1. Под SELECT FOR UPDATE резервирует места и создаёт Booking (pending_payment).
        2. Запускает Protection API конкурентно (create_task), а Payment API дожидается напрямую —
           Payment всегда нужен сразу, поэтому не должен зависеть от скорости Protection.
        3. Protection ждём не больше 3 секунд (asyncio.wait_for). Если не успели/ошибка —
           отвечаем без страховки и ставим фоновую задачу get_protection_price на досчёт.
        4. Комиссия платежа сохраняется всегда; поля страховки — только если она успела.
        """
        try:
            if not (event := await self.db_manager.event_repo.get_by_id(event_id=event_id)):
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

        protection_task = asyncio.create_task(self.protection_connector.calculate(protection_payload))

        try:
            payment_quote = await self.payment_connector.calculate(payload=payment_payload)
        except PaymentNotAvailableError:
            await self._cancel_reservation(booking, seats)
            protection_task.cancel()
            raise

        try:
            protection_quote = await asyncio.wait_for(protection_task, timeout=3.0)
        except (httpx.NetworkError, httpx.TimeoutException, httpx.HTTPStatusError, TimeoutError):
            await get_protection_price.kiq(protection_payload)
            protection_quote = None

        if protection_quote:
            booking.protection_price = protection_quote.price
            booking.with_protection = True
        booking.payment_commission = payment_quote.commission
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
    
    async def cancel_expired_bookings(self) -> dict:
        all_bookings = await self.db_manager.booking_repo.get_list()
        now = datetime.now(UTC).replace(tzinfo=None)
        deleted_count = 0

        for obj in all_bookings:
            if obj.status == BookingStatus.pending_payment and obj.reserved_until < now:
                async with self.db_manager.transaction() as db_manager:
                    event_seats = await db_manager.event_seat_repo.get_event_seats_by_booking_id(obj.id)
                    for event_seat in event_seats:
                        event_seat.status = SeatStatus.available
                        event_seat.booking_id = None
                        event_seat.reserved_until = None

                    await db_manager.session.flush()
                    await db_manager.booking_repo.delete_by_id(obj.id)
                deleted_count += 1

        return {"deleted_count": deleted_count}
        
    async def _cancel_reservation(self, booking: Booking, seats: list[EventSeat]) -> None:
        booking.status = BookingStatus.cancelled

        for seat in seats:
            seat.status = SeatStatus.available
            seat.reserved_until = None
            seat.booking_id = None
        await self.db_manager.session.commit()