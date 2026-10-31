from dataclasses import dataclass


@dataclass(frozen=True)
class OutboxConfig:
    poll_interval_seconds: float = 1.0
    batch_size: int = 100
