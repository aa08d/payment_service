from dataclasses import dataclass, field
from urllib.parse import quote


@dataclass
class DBConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "payment"
    user: str = "payment"
    password: str = field(default="payment", repr=False)
    pool_size: int = 10
    echo: bool = False

    @property
    def full_url(self) -> str:
        user = quote(self.user, safe="")
        password = quote(self.password, safe="")
        return f"postgresql+asyncpg://{user}:{password}@{self.host}:{self.port}/{self.database}"
