import logging

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from payment.domain.common.exceptions import AppError

from .auth import build_api_key_dependency
from .config import ApiConfig
from .routes import router

logger = logging.getLogger(__name__)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    if exc.status >= 500:
        logger.error("Application error", exc_info=exc)

    return JSONResponse(status_code=exc.status, content={"code": type(exc).__name__, "detail": exc.message})


def create_api(config: ApiConfig) -> FastAPI:
    app = FastAPI(title="Payment processing service", version="1.0.0")

    app.include_router(router, dependencies=[Depends(build_api_key_dependency(config.api_key))])
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]

    @app.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
