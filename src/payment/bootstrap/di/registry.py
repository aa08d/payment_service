from payment.application.common.mediator import MediatorRegistry


def build_mediator_registry() -> MediatorRegistry:
    registry = MediatorRegistry()

    # registry.register_request(CreateThingCommand, CreateThingHandler)
    # registry.register_event(ThingCreated, SomeEventHandler)

    return registry  # noqa: RET504
