from uuid import UUID

import pytest

from payment.application.payment.commands import ProcessPaymentCommand, ProcessPaymentHandler
from payment.application.payment.exceptions import PaymentNotExistsError
from payment.application.payment.interfaces.gateway import GatewayResult
from payment.domain.payment.events import PaymentFailed, PaymentSucceeded
from payment.domain.payment.value_objects import PaymentStatus
from tests.factories import create_payment
from tests.mocks import GatewayCall, MediatorMock, PaymentGatewayMock, PaymentRepositoryMock, UnitOfWorkMock


async def test_process_payment_handler_approved(
    payment_repo: PaymentRepositoryMock,
    gateway: PaymentGatewayMock,
    uow: UnitOfWorkMock,
    mediator: MediatorMock,
) -> None:
    handler = ProcessPaymentHandler(payment_repo, gateway, uow, mediator)
    payment = create_payment()
    await payment_repo.save(payment)
    gateway.result = GatewayResult.approve()

    await handler(ProcessPaymentCommand(payment_id=payment.payment_id.value))

    assert gateway.calls == [
        GatewayCall(payment_id=payment.payment_id.value, amount=payment.money.amount, currency="RUB"),
    ]

    assert payment.status is PaymentStatus.succeeded
    assert payment.timestamps.processed_at is not None

    assert len(mediator.published_events) == 1
    published_event = mediator.published_events[0]
    assert isinstance(published_event, PaymentSucceeded)
    assert published_event.payment_id == payment.payment_id.value
    assert published_event.idempotency_key == payment.idempotency_key.value
    assert published_event.amount == payment.money.amount
    assert published_event.currency == "RUB"
    assert published_event.webhook_url == payment.webhook_url.value
    assert published_event.status == "succeeded"
    assert published_event.processed_at == payment.timestamps.processed_at
    assert published_event.metadata == payment.metadata

    assert uow.committed is True
    assert uow.rolled_back is False


async def test_process_payment_handler_declined(
    payment_repo: PaymentRepositoryMock,
    gateway: PaymentGatewayMock,
    uow: UnitOfWorkMock,
    mediator: MediatorMock,
) -> None:
    handler = ProcessPaymentHandler(payment_repo, gateway, uow, mediator)
    payment = create_payment()
    await payment_repo.save(payment)
    gateway.result = GatewayResult.decline()

    await handler(ProcessPaymentCommand(payment_id=payment.payment_id.value))

    assert len(gateway.calls) == 1
    assert payment.status is PaymentStatus.failed
    assert payment.timestamps.processed_at is not None

    assert len(mediator.published_events) == 1
    published_event = mediator.published_events[0]
    assert isinstance(published_event, PaymentFailed)
    assert published_event.payment_id == payment.payment_id.value
    assert published_event.status == "failed"
    assert published_event.processed_at == payment.timestamps.processed_at

    assert uow.committed is True
    assert uow.rolled_back is False


@pytest.mark.parametrize("approved", [True, False], ids=["succeeded", "failed"])
async def test_process_payment_handler_already_processed_payment_is_skipped(
    approved: bool,
    payment_repo: PaymentRepositoryMock,
    gateway: PaymentGatewayMock,
    uow: UnitOfWorkMock,
    mediator: MediatorMock,
) -> None:
    handler = ProcessPaymentHandler(payment_repo, gateway, uow, mediator)
    payment = create_payment()
    if approved:
        payment.succeed()
    else:
        payment.fail()
    payment.clear_events()
    await payment_repo.save(payment)
    status = payment.status
    processed_at = payment.timestamps.processed_at

    await handler(ProcessPaymentCommand(payment_id=payment.payment_id.value))

    assert gateway.calls == []
    assert payment.status is status
    assert payment.timestamps.processed_at == processed_at
    assert len(mediator.published_events) == 0
    assert uow.committed is False
    assert uow.rolled_back is False


async def test_process_payment_handler_payment_not_found(
    payment_repo: PaymentRepositoryMock,
    gateway: PaymentGatewayMock,
    uow: UnitOfWorkMock,
    mediator: MediatorMock,
) -> None:
    handler = ProcessPaymentHandler(payment_repo, gateway, uow, mediator)
    payment_id = UUID("123e4567-e89b-12d3-a456-426614174099")

    with pytest.raises(PaymentNotExistsError) as exc_info:
        await handler(ProcessPaymentCommand(payment_id=payment_id))

    assert exc_info.value.status == 404
    assert gateway.calls == []
    assert len(mediator.published_events) == 0
    assert uow.committed is False


async def test_process_payment_handler_gateway_error_leaves_payment_pending(
    payment_repo: PaymentRepositoryMock,
    gateway: PaymentGatewayMock,
    uow: UnitOfWorkMock,
    mediator: MediatorMock,
) -> None:
    handler = ProcessPaymentHandler(payment_repo, gateway, uow, mediator)
    payment = create_payment()
    await payment_repo.save(payment)
    gateway.error = ConnectionError("gateway is unavailable")

    with pytest.raises(ConnectionError):
        await handler(ProcessPaymentCommand(payment_id=payment.payment_id.value))

    assert payment.status is PaymentStatus.pending
    assert payment.timestamps.processed_at is None
    assert len(mediator.published_events) == 0
    assert uow.committed is False
