from dishka import AsyncContainer, Provider, Scope, provide

from payment.application.common.mediator import Mediator, MediatorRegistry

from .mediator import DishkaMediator
from .registry import build_mediator_registry


class MediatorProvider(Provider):
    @provide(scope=Scope.APP)
    def mediator_registry(self) -> MediatorRegistry:
        return build_mediator_registry()

    @provide(scope=Scope.REQUEST)
    def mediator(self, registry: MediatorRegistry, container: AsyncContainer) -> Mediator:
        return DishkaMediator(registry, container)

    # Register command/query/event handlers here, e.g.:
    # create_thing_handler = provide(CreateThingHandler, scope=Scope.REQUEST)


def get_providers() -> list[Provider]:
    return [MediatorProvider()]
