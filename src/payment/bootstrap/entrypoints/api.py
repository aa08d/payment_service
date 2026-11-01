import logging

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from payment.bootstrap.config import AppConfig, load_app_config
from payment.bootstrap.di import get_providers
from payment.presentation.api.app import create_api


def create_app(config: AppConfig | None = None) -> FastAPI:
    config = config or load_app_config()

    app = create_api(config.api)

    container = make_async_container(*get_providers(), context={AppConfig: config})
    setup_dishka(container, app)

    return app


def app_factory() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return create_app()
