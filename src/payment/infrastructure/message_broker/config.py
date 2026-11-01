from dataclasses import dataclass
from urllib.parse import quote


@dataclass(frozen=True, slots=True)
class RabbitConfig:
    host: str = "localhost"
    port: int = 5672
    user: str = "guest"
    password: str = "guest"
    vhost: str = "/"

    @property
    def url(self) -> str:
        user = quote(self.user, safe="")
        password = quote(self.password, safe="")
        vhost = quote(self.vhost, safe="")
        return f"amqp://{user}:{password}@{self.host}:{self.port}/{vhost}"


@dataclass(frozen=True, slots=True)
class ConsumerConfig:
    prefetch_count: int = 10
    max_attempts: int = 3
    retry_base_delay_seconds: float = 2.0
