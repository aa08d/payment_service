from payment.application.common.mediator import MediatorRegistry
from payment.application.payment.commands import (
    CreatePaymentCommand,
    CreatePaymentHandler,
    ProcessPaymentCommand,
    ProcessPaymentHandler,
)
from payment.application.payment.events import SendWebhookEvent, SendWebhookHandler
from payment.application.payment.queries import GetPaymentByIdQuery, GetPaymentByIdQueryHandler
from payment.domain.payment.events import PaymentCreated, PaymentFailed, PaymentSucceeded
from payment.infrastructure.outbox.handler import OutboxEventHandler


def build_mediator_registry() -> MediatorRegistry:
    registry = MediatorRegistry()

    registry.register_request(CreatePaymentCommand, CreatePaymentHandler)
    registry.register_request(ProcessPaymentCommand, ProcessPaymentHandler)
    registry.register_request(GetPaymentByIdQuery, GetPaymentByIdQueryHandler)

    for event in (PaymentCreated, PaymentSucceeded, PaymentFailed):
        registry.register_event(event, OutboxEventHandler)

    registry.register_event(SendWebhookEvent, SendWebhookHandler)

    return registry
