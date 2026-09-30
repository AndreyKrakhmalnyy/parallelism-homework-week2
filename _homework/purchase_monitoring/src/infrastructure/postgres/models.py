from datetime import datetime
import uuid

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseDBModel(DeclarativeBase):
    __abstract__ = True


class EventPaymentActivity(BaseDBModel):
    __tablename__ = "event_payment_activity"

    id: Mapped[int] = mapped_column(primary_key=True)
    batch_id: Mapped[uuid.UUID]
    event_id: Mapped[int] = mapped_column(index=True, unique=True)
    payments_count: Mapped[int]
    tickets_count: Mapped[int]
    total_amount: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime())