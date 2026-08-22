from sqlalchemy.orm import DeclarativeBase


class BaseDBModel(DeclarativeBase):
    __abstract__ = True


class PurchaseTicket(BaseDBModel):
    pass