import secrets
from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def build_api_key_dependency(expected_key: str) -> Callable[..., Awaitable[None]]:
    async def verify_api_key(api_key: str | None = Security(api_key_header)) -> None:
        if api_key is None or not secrets.compare_digest(api_key.encode(), expected_key.encode()):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")

    return verify_api_key
