from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseDBModel(DeclarativeBase):
    __abstract__ = True


class PurchaseTicket(BaseDBModel):
    __tablename__ = "purchase_tickets"

    id: Mapped[int] = mapped_column(primary_key=True)