from dishka import make_async_container

from payment.application.common.mediator import Mediator
from payment.bootstrap.di import DishkaMediator, get_providers


async def test_mediator_is_resolved_from_container() -> None:
    container = make_async_container(*get_providers())
    async with container() as request_container:
        assert isinstance(await request_container.get(Mediator), DishkaMediator)
    await container.close()
