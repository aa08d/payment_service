from dataclasses import FrozenInstanceError, dataclass
from datetime import UTC, datetime

import pytest

from payment.domain.common.events import Event


@dataclass(frozen=True)
class SomethingHappened(Event):
    number: int


def test_event_gets_id_and_utc_timestamp_automatically() -> None:
    before = datetime.now(UTC)
    event = SomethingHappened(number=1)
    after = datetime.now(UTC)

    assert event.event_id.version == 7
    assert event.event_timestamp.tzinfo is UTC
    assert before <= event.event_timestamp <= after


def test_events_get_different_ids() -> None:
    assert SomethingHappened(number=1).event_id != SomethingHappened(number=1).event_id


def test_event_id_and_timestamp_cannot_be_passed_explicitly() -> None:
    with pytest.raises(TypeError):
        SomethingHappened(number=1, event_timestamp=datetime.now(UTC))  # type: ignore[call-arg]


def test_event_is_immutable() -> None:
    event = SomethingHappened(number=1)

    with pytest.raises(FrozenInstanceError):
        event.number = 2  # type: ignore[misc]
