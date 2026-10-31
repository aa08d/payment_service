import pytest

from tests.mocks import (
    MediatorMock,
    PaymentGatewayMock,
    PaymentReaderMock,
    PaymentRepositoryMock,
    UnitOfWorkMock,
    WebhookNotifierMock,
)


@pytest.fixture
def payment_repo() -> PaymentRepositoryMock:
    return PaymentRepositoryMock()


@pytest.fixture
def payment_reader() -> PaymentReaderMock:
    return PaymentReaderMock()


@pytest.fixture
def gateway() -> PaymentGatewayMock:
    return PaymentGatewayMock()


@pytest.fixture
def notifier() -> WebhookNotifierMock:
    return WebhookNotifierMock()


@pytest.fixture
def mediator() -> MediatorMock:
    return MediatorMock()


@pytest.fixture
def uow() -> UnitOfWorkMock:
    return UnitOfWorkMock()
