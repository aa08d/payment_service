from uuid import UUID, uuid7

from payment.domain.payment.value_objects import IdempotencyKey, PaymentID


def test_payment_id_create_generates_uuid_v7() -> None:
    payment_id = PaymentID.create()

    assert isinstance(payment_id.value, UUID)
    assert payment_id.value.version == 7


def test_payment_id_create_generates_unique_ids() -> None:
    payment_ids = {PaymentID.create() for _ in range(100)}

    assert len(payment_ids) == 100


def test_payment_id_equality_and_hash_depend_on_value() -> None:
    value = uuid7()

    assert PaymentID(value) == PaymentID(value)
    assert hash(PaymentID(value)) == hash(PaymentID(value))
    assert PaymentID(value) != PaymentID(uuid7())
    assert {PaymentID(value): "payment"}[PaymentID(value)] == "payment"


def test_idempotency_key_equality_and_hash_depend_on_value() -> None:
    value = uuid7()

    assert IdempotencyKey(value) == IdempotencyKey(value)
    assert hash(IdempotencyKey(value)) == hash(IdempotencyKey(value))
    assert IdempotencyKey(value) != IdempotencyKey(uuid7())


def test_payment_id_and_idempotency_key_are_different_types() -> None:
    value = uuid7()

    assert PaymentID(value) != IdempotencyKey(value)
