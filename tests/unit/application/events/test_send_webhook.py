from uuid import UUID

import pytest

from payment.application.payment.events import SendWebhookEvent, SendWebhookHandler
from payment.application.payment.exceptions import PaymentNotExistsError, WebhookDeliveryError
from tests.factories import PAYMENT_ID, create_payment_detail
from tests.mocks import PaymentReaderMock, WebhookNotifierMock


async def test_send_webhook_handler_notifies_with_current_payment_state(
    payment_reader: PaymentReaderMock,
    notifier: WebhookNotifierMock,
) -> None:
    handler = SendWebhookHandler(payment_reader, notifier)
    payment = create_payment_detail(status="failed")
    await payment_reader.add_payment(payment)

    await handler(SendWebhookEvent(payment_id=PAYMENT_ID))

    assert notifier.notified == [payment]


async def test_send_webhook_handler_payment_not_found(
    payment_reader: PaymentReaderMock,
    notifier: WebhookNotifierMock,
) -> None:
    handler = SendWebhookHandler(payment_reader, notifier)

    with pytest.raises(PaymentNotExistsError):
        await handler(SendWebhookEvent(payment_id=UUID("123e4567-e89b-12d3-a456-426614174099")))

    assert notifier.notified == []


async def test_send_webhook_handler_delivery_error_is_propagated_for_retry(
    payment_reader: PaymentReaderMock,
    notifier: WebhookNotifierMock,
) -> None:
    handler = SendWebhookHandler(payment_reader, notifier)
    payment = create_payment_detail()
    await payment_reader.add_payment(payment)
    notifier.error = WebhookDeliveryError(payment.webhook_url)

    with pytest.raises(WebhookDeliveryError) as exc_info:
        await handler(SendWebhookEvent(payment_id=PAYMENT_ID))

    assert exc_info.value.status == 502
    assert payment.webhook_url in exc_info.value.message
    assert notifier.notified == []
