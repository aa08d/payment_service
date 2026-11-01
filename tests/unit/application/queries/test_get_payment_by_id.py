from uuid import UUID

import pytest

from payment.application.payment.exceptions import PaymentNotExistsError
from payment.application.payment.queries import GetPaymentByIdQuery, GetPaymentByIdQueryHandler
from tests.factories import PAYMENT_ID, create_payment_detail
from tests.mocks import PaymentReaderMock


async def test_get_payment_by_id_handler(payment_reader: PaymentReaderMock) -> None:
    payment = create_payment_detail()
    await payment_reader.add_payment(payment)
    handler = GetPaymentByIdQueryHandler(payment_reader)

    result = await handler(GetPaymentByIdQuery(payment_id=PAYMENT_ID))

    assert result == payment


async def test_get_payment_by_id_handler_payment_not_found(payment_reader: PaymentReaderMock) -> None:
    await payment_reader.add_payment(create_payment_detail())
    handler = GetPaymentByIdQueryHandler(payment_reader)

    non_existent_payment_id = UUID("00000000-0000-0000-0000-000000000000")

    with pytest.raises(PaymentNotExistsError) as exc_info:
        await handler(GetPaymentByIdQuery(payment_id=non_existent_payment_id))

    assert exc_info.value.status == 404
    assert str(non_existent_payment_id) in exc_info.value.message
