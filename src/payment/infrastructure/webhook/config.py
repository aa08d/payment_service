from dataclasses import dataclass


@dataclass
class WebhookConfig:
    timeout_seconds: float = 5.0
