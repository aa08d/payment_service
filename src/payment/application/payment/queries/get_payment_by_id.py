import logging
from dataclasses import dataclass
from uuid import UUID

from payment.application.common.queries import Query, QueryHandler
from payment.application.payment.dto import PaymentDetailDTO
from payment.application.payment.exceptions import PaymentNotExistsError
from payment.application.payment.interfaces.persistence import PaymentReader

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetPaymentByIdQuery(Query[PaymentDetailDTO]):
    payment_id: UUID


class GetPaymentByIdQueryHandler(QueryHandler[GetPaymentByIdQuery, PaymentDetailDTO]):
    def __init__(self, payment_reader: PaymentReader) -> None:
        self._payment_reader = payment_reader

    async def __call__(self, query: GetPaymentByIdQuery) -> PaymentDetailDTO:
        payment = await self._payment_reader.get_payment_by_id(query.payment_id)

        if payment is None:
            raise PaymentNotExistsError(query.payment_id)

        logger.debug(
            "Get payment by ID",
            extra={
                "payment_id": query.payment_id,
                "payment": payment,
            },
        )

        return payment
