import httpx

from payment.application.payment.dto import PaymentDetailDTO
from payment.application.payment.exceptions import WebhookDeliveryError
from payment.application.payment.interfaces import WebhookNotifier


class HttpWebhookNotifier(WebhookNotifier):
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def notify(self, payment: PaymentDetailDTO) -> None:
        url = payment.webhook_url
        payload = {
            "payment_id": str(payment.payment_id),
            "idempotency_key": str(payment.idempotency_key),
            "status": payment.status,
            "amount": str(payment.amount),
            "currency": payment.currency,
            "description": payment.description,
            "metadata": payment.metadata,
            "created_at": payment.created_at.isoformat(),
            "processed_at": payment.processed_at.isoformat() if payment.processed_at else None,
        }

        try:
            response = await self._client.post(url, json=payload, headers={"X-Payment-Id": str(payment.payment_id)})
        except httpx.HTTPError as err:
            raise WebhookDeliveryError(url) from err

        if not response.is_success:
            raise WebhookDeliveryError(url)
