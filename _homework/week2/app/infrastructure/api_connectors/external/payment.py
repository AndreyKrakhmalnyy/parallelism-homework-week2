from app.api.schemas.payment import PaymentPayIn, PaymentPayOut, PaymentQuoteIn, PaymentQuoteOut
from app.infrastructure.api_connectors.base import BaseHTTPConnector


class PaymentConnector(BaseHTTPConnector):
    async def calculate(self, payload: PaymentQuoteIn) -> PaymentQuoteOut:
        response = await self.request(
            "POST", 
            "/payment/calculate",
            json=payload.model_dump()
        )
        response.raise_for_status()
        return PaymentQuoteOut.model_validate(response.json())

    async def pay(self, payload: PaymentPayIn) -> PaymentPayOut:
        response = await self.request(
            "POST",
            "/payment/pay",
            json=payload.model_dump()
        )
        response.raise_for_status()
        return PaymentPayOut.model_validate(response.json())
