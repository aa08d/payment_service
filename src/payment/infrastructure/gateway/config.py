from dataclasses import dataclass


@dataclass
class GatewayConfig:
    min_delay_seconds: float = 2.0
    max_delay_seconds: float = 5.0
    success_rate: float = 0.9
