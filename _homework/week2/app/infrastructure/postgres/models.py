from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from app.domain.enums import BookingStatus, SeatStatus
from sqlalchemy import ForeignKey, UniqueConstraint, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column



class BaseDBModel(DeclarativeBase):
    __abstract__ = True

class Seat(BaseDBModel):
    """Место на площадке."""

    __tablename__ = "seats"
    __table_args__ = (
        UniqueConstraint("location_id", "sector", "row", "number", name="uq_seat_position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), index=True)
    sector: Mapped[str] = mapped_column(index=True)
    row: Mapped[int]
    number: Mapped[int]
    x: Mapped[int]
    y: Mapped[int]

class Location(BaseDBModel):
    """Площадка, где проходят мероприятия (например, Лужники, ВТБ-Арена)."""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    city: Mapped[str]
    address: Mapped[str]

class Event(BaseDBModel):
    """Мероприятие с датой, площадкой и базовой ценой. Создается организатором.
        Например: Концерт Аллы Пугачевой, Мастер-класс по Python."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    organizer_id: Mapped[int] = mapped_column(index=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), index=True)
    title: Mapped[str]
    description: Mapped[str | None]
    category: Mapped[str]
    starts_at: Mapped[datetime] = mapped_column(DateTime(), index=True)
    base_price: Mapped[int]

class EventSeat(BaseDBModel):
    """Место конкретного мероприятия с ценой и статусом."""

    __tablename__ = "event_seats"
    __table_args__ = (
        UniqueConstraint("event_id", "seat_id", name="uq_event_seat"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    seat_id: Mapped[int] = mapped_column(ForeignKey("seats.id"), index=True)
    price: Mapped[int]
    status: Mapped[SeatStatus] = mapped_column(
        SAEnum(SeatStatus, name="seat_status"),
        default=SeatStatus.available,
        server_default=SeatStatus.available.value,
        index=True,
    )
    reserved_until: Mapped[datetime | None] = mapped_column(DateTime())
    booking_id: Mapped[int | None] = mapped_column(
        ForeignKey("bookings.id"),
        index=True,
    )

class Booking(BaseDBModel):
    """Бронь пользователя на выбранные места."""

    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    user_id: Mapped[int] = mapped_column(index=True)
    amount: Mapped[int]  # суммарная стоимость всех выбранных мест
    payment_commission: Mapped[int]
    protection_price: Mapped[int | None]
    with_protection: Mapped[bool]
    status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus, name="booking_status"),
        default=BookingStatus.pending_payment,
        server_default=BookingStatus.pending_payment.value,
        index=True,
    )
    reserved_until: Mapped[datetime] = mapped_column(DateTime(), index=True)

