from dataclasses import dataclass


@dataclass
class ApiConfig:
    api_key: str
    host: str = "0.0.0.0"
    port: int = 8000
