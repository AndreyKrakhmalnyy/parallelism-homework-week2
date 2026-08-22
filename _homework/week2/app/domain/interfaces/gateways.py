from typing import Protocol

from app.api.schemas.payment import PaymentQuoteIn, PaymentQuoteOut
from app.api.schemas.protection import ProtectionQuoteIn, ProtectionQuoteOut


class PaymentGatewayPort(Protocol):
    async def calculate(self, payload: PaymentQuoteIn) -> PaymentQuoteOut: ...


class ProtectionGatewayPort(Protocol):
    async def calculate(self, payload: ProtectionQuoteIn) -> ProtectionQuoteOut: ...
