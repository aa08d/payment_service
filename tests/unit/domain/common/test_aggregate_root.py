from dataclasses import dataclass

from payment.domain.common.entities import AggregateRoot
from payment.domain.common.events import Event


@dataclass(frozen=True)
class SomethingHappened(Event):
    number: int


class SomeAggregate(AggregateRoot):
    pass


def test_aggregate_has_no_events_by_default() -> None:
    assert SomeAggregate().pull_events() == []


def test_aggregate_returns_events_in_recorded_order_and_forgets_them() -> None:
    aggregate = SomeAggregate()
    first, second = SomethingHappened(number=1), SomethingHappened(number=2)
    aggregate.record_event(first)
    aggregate.record_event(second)

    assert aggregate.pull_events() == [first, second]
    assert aggregate.pull_events() == []


def test_aggregate_pulled_events_are_a_copy() -> None:
    aggregate = SomeAggregate()
    aggregate.record_event(SomethingHappened(number=1))

    pulled = aggregate.pull_events()
    pulled.append(SomethingHappened(number=2))

    assert aggregate.pull_events() == []


def test_aggregate_clear_events() -> None:
    aggregate = SomeAggregate()
    aggregate.record_event(SomethingHappened(number=1))

    aggregate.clear_events()

    assert aggregate.pull_events() == []


def test_aggregates_do_not_share_events() -> None:
    first, second = SomeAggregate(), SomeAggregate()

    first.record_event(SomethingHappened(number=1))

    assert second.pull_events() == []
