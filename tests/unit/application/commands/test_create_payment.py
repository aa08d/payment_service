from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest

from payment.application.payment.commands import CreatePaymentHandler
from payment.application.payment.exceptions import IdempotencyKeyConflictError
from payment.domain.payment.events import PaymentCreated
from payment.domain.payment.value_objects import Currency, IdempotencyKey, PaymentStatus
from payment.domain.payment.value_objects.description import TooLongDescriptionError
from payment.domain.payment.value_objects.money import NonPositiveAmountError
from payment.domain.payment.value_objects.webhook_url import InvalidWebhookURLError
from tests.factories import IDEMPOTENCY_KEY, create_payment, create_payment_command
from tests.mocks import MediatorMock, PaymentRepositoryMock, UnitOfWorkMock


async def test_create_payment_handler_success(
    payment_repo: PaymentRepositoryMock,
    uow: UnitOfWorkMock,
    mediator: MediatorMock,
) -> None:
    handler = CreatePaymentHandler(payment_repo, uow, mediator)
    command = create_payment_command()

    result = await handler(command)

    assert len(payment_repo.payments) == 1
    payment = next(iter(payment_repo.payments.values()))

    assert result.payment_id == payment.payment_id.value
    assert result.status == "pending"
    assert result.created_at == payment.timestamps.created_at

    assert payment.idempotency_key == IdempotencyKey(command.idempotency_key)
    assert payment.money.amount == command.amount
    assert payment.money.currency == command.currency
    assert payment.description.value == command.description
    assert payment.webhook_url.value == command.webhook_url
    assert payment.metadata == command.metadata
    assert payment.status is PaymentStatus.pending
    assert payment.timestamps.processed_at is None

    assert len(mediator.published_events) == 1
    published_event = mediator.published_events[0]
    assert isinstance(published_event, PaymentCreated)
    assert published_event.payment_id == payment.payment_id.value
    assert published_event.idempotency_key == command.idempotency_key
    assert published_event.amount == command.amount
    assert published_event.currency == command.currency
    assert published_event.description == command.description
    assert published_event.webhook_url == command.webhook_url
    assert published_event.status == "pending"
    assert published_event.metadata == command.metadata

    assert payment.pull_events() == []
    assert uow.committed is True
    assert uow.rolled_back is False


async def test_create_payment_handler_repeated_request_returns_existing_payment(
    payment_repo: PaymentRepositoryMock,
    uow: UnitOfWorkMock,
    mediator: MediatorMock,
) -> None:
    handler = CreatePaymentHandler(payment_repo, uow, mediator)
    existing = create_payment()
    await payment_repo.save(existing)

    result = await handler(create_payment_command())

    assert result.payment_id == existing.payment_id.value
    assert result.status == "pending"
    assert result.created_at == existing.timestamps.created_at

    assert list(payment_repo.payments.values()) == [existing]
    assert len(mediator.published_events) == 0
    assert uow.committed is False
    assert uow.rolled_back is True


async def test_create_payment_handler_repeated_request_returns_current_status(
    payment_repo: PaymentRepositoryMock,
    uow: UnitOfWorkMock,
    mediator: MediatorMock,
) -> None:
    handler = CreatePaymentHandler(payment_repo, uow, mediator)
    existing = create_payment()
    existing.succeed()
    existing.clear_events()
    await payment_repo.save(existing)

    result = await handler(create_payment_command())

    assert result.payment_id == existing.payment_id.value
    assert result.status == "succeeded"
    assert len(mediator.published_events) == 0
    assert uow.committed is False


@pytest.mark.parametrize(
    "changes",
    [
        {"amount": Decimal("1500.01")},
        {"currency": Currency.USD},
        {"description": "Another order"},
        {"webhook_url": "https://example.com/another-webhook"},
        {"metadata": {"order_id": 124}},
    ],
    ids=["amount", "currency", "description", "webhook_url", "metadata"],
)
async def test_create_payment_handler_same_key_with_different_parameters(
    changes: dict[str, Any],
    payment_repo: PaymentRepositoryMock,
    uow: UnitOfWorkMock,
    mediator: MediatorMock,
) -> None:
    handler = CreatePaymentHandler(payment_repo, uow, mediator)
    existing = create_payment()
    await payment_repo.save(existing)

    with pytest.raises(IdempotencyKeyConflictError) as exc_info:
        await handler(create_payment_command(**changes))

    assert exc_info.value.status == 409
    assert str(IDEMPOTENCY_KEY) in exc_info.value.message
    assert list(payment_repo.payments.values()) == [existing]
    assert len(mediator.published_events) == 0
    assert uow.committed is False


async def test_create_payment_handler_same_key_equal_amount_with_different_scale(
    payment_repo: PaymentRepositoryMock,
    uow: UnitOfWorkMock,
    mediator: MediatorMock,
) -> None:
    handler = CreatePaymentHandler(payment_repo, uow, mediator)
    existing = create_payment(amount=Decimal("1500.00"))
    await payment_repo.save(existing)

    result = await handler(create_payment_command(amount=Decimal("1500")))

    assert result.payment_id == existing.payment_id.value
    assert len(mediator.published_events) == 0


async def test_create_payment_handler_different_keys_create_different_payments(
    payment_repo: PaymentRepositoryMock,
    uow: UnitOfWorkMock,
    mediator: MediatorMock,
) -> None:
    handler = CreatePaymentHandler(payment_repo, uow, mediator)
    existing = create_payment()
    await payment_repo.save(existing)
    other_key = UUID(int=existing.idempotency_key.value.int + 1)

    result = await handler(create_payment_command(idempotency_key=other_key))

    assert result.payment_id != existing.payment_id.value
    assert len(payment_repo.payments) == 2
    assert len(mediator.published_events) == 1
    assert uow.committed is True


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        ({"amount": Decimal("0")}, NonPositiveAmountError),
        ({"description": "x" * 251}, TooLongDescriptionError),
        ({"webhook_url": "ftp://example.com/webhook"}, InvalidWebhookURLError),
    ],
    ids=["amount", "description", "webhook_url"],
)
async def test_create_payment_handler_invalid_input(
    changes: dict[str, Any],
    error: type[Exception],
    payment_repo: PaymentRepositoryMock,
    uow: UnitOfWorkMock,
    mediator: MediatorMock,
) -> None:
    handler = CreatePaymentHandler(payment_repo, uow, mediator)

    with pytest.raises(error):
        await handler(create_payment_command(**changes))

    assert payment_repo.payments == {}
    assert len(mediator.published_events) == 0
    assert uow.committed is False
    assert uow.rolled_back is False
