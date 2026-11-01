from collections.abc import AsyncIterator

import httpx
from dishka import AsyncContainer, Provider, Scope, from_context, provide
from faststream.rabbit import RabbitBroker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from payment.application.common.interfaces import UnitOfWork
from payment.application.common.mediator import Mediator, MediatorRegistry
from payment.application.payment.commands import CreatePaymentHandler, ProcessPaymentHandler
from payment.application.payment.events import SendWebhookHandler
from payment.application.payment.interfaces import PaymentGateway, WebhookNotifier
from payment.application.payment.interfaces.persistence import PaymentReader
from payment.application.payment.queries import GetPaymentByIdQueryHandler
from payment.bootstrap.config import AppConfig
from payment.domain.payment.repositories import PaymentRepository
from payment.infrastructure.database.config import DBConfig
from payment.infrastructure.database.main import build_sa_engine, build_sa_session_factory
from payment.infrastructure.database.readers import PaymentSQLAlchemyReader
from payment.infrastructure.database.repositories import PaymentSQLAlchemyRepository
from payment.infrastructure.database.uow import SQLAlchemyUoW
from payment.infrastructure.gateway import EmulatedPaymentGateway, GatewayConfig
from payment.infrastructure.message_broker.config import ConsumerConfig, RabbitConfig
from payment.infrastructure.outbox import (
    OutboxConfig,
    OutboxEventHandler,
    OutboxMessageMapper,
    OutboxRelay,
    OutboxSQLAlchemyRepository,
    RabbitMessagePublisher,
)
from payment.infrastructure.outbox.interfaces import MessagePublisher, OutboxRepository
from payment.infrastructure.webhook import HttpWebhookNotifier, WebhookConfig

from .mediator import DishkaMediator
from .registry import build_mediator_registry


class ConfigProvider(Provider):
    scope = Scope.APP
    config = from_context(AppConfig, scope=Scope.APP)

    @provide
    def db_config(self, config: AppConfig) -> DBConfig:
        return config.db

    @provide
    def rabbit_config(self, config: AppConfig) -> RabbitConfig:
        return config.rabbit

    @provide
    def consumer_config(self, config: AppConfig) -> ConsumerConfig:
        return config.consumer

    @provide
    def gateway_config(self, config: AppConfig) -> GatewayConfig:
        return config.gateway

    @provide
    def webhook_config(self, config: AppConfig) -> WebhookConfig:
        return config.webhook

    @provide
    def outbox_config(self, config: AppConfig) -> OutboxConfig:
        return config.outbox


class InfrastructureProvider(Provider):
    scope = Scope.APP
    broker = from_context(RabbitBroker, scope=Scope.APP)

    @provide
    async def engine(self, db_config: DBConfig) -> AsyncIterator[AsyncEngine]:
        async with build_sa_engine(db_config) as engine:
            yield engine

    @provide
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return build_sa_session_factory(engine)

    @provide
    async def http_client(self, config: WebhookConfig) -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient(timeout=config.timeout_seconds, follow_redirects=False) as client:
            yield client

    @provide
    def mediator_registry(self) -> MediatorRegistry:
        return build_mediator_registry()

    @provide
    def outbox_mapper(self) -> OutboxMessageMapper:
        return OutboxMessageMapper()

    gateway = provide(EmulatedPaymentGateway, provides=PaymentGateway)
    webhook_notifier = provide(HttpWebhookNotifier, provides=WebhookNotifier)
    message_publisher = provide(RabbitMessagePublisher, provides=MessagePublisher)


class RequestProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def session(self, session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    uow = provide(SQLAlchemyUoW, provides=UnitOfWork)

    payment_repository = provide(PaymentSQLAlchemyRepository, provides=PaymentRepository)
    outbox_repository = provide(OutboxSQLAlchemyRepository, provides=OutboxRepository)
    payment_reader = provide(PaymentSQLAlchemyReader, provides=PaymentReader)

    @provide
    def mediator(self, registry: MediatorRegistry, container: AsyncContainer) -> Mediator:
        return DishkaMediator(registry, container)

    @provide
    def outbox_relay(
        self,
        repository: OutboxRepository,
        publisher: MessagePublisher,
        uow: UnitOfWork,
        config: OutboxConfig,
    ) -> OutboxRelay:
        return OutboxRelay(repository, publisher, uow, config.batch_size)

    create_payment_handler = provide(CreatePaymentHandler)
    process_payment_handler = provide(ProcessPaymentHandler)
    send_webhook_handler = provide(SendWebhookHandler)
    get_payment_by_id_handler = provide(GetPaymentByIdQueryHandler)
    outbox_handler = provide(OutboxEventHandler)


def get_providers() -> tuple[Provider, ...]:
    return ConfigProvider(), InfrastructureProvider(), RequestProvider()
