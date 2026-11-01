from dataclasses import dataclass, field

from payment.infrastructure.database.config import DBConfig
from payment.infrastructure.gateway.config import GatewayConfig
from payment.infrastructure.message_broker.config import ConsumerConfig, RabbitConfig
from payment.infrastructure.outbox.config import OutboxConfig
from payment.infrastructure.webhook.config import WebhookConfig
from payment.presentation.api.config import ApiConfig

from .config_loader import load_config


@dataclass
class AppConfig:
    api: ApiConfig
    db: DBConfig = field(default_factory=DBConfig)
    rabbit: RabbitConfig = field(default_factory=RabbitConfig)
    consumer: ConsumerConfig = field(default_factory=ConsumerConfig)
    gateway: GatewayConfig = field(default_factory=GatewayConfig)
    webhook: WebhookConfig = field(default_factory=WebhookConfig)
    outbox: OutboxConfig = field(default_factory=OutboxConfig)


def load_app_config(path: str | None = None) -> AppConfig:
    return load_config(AppConfig, path=path)
