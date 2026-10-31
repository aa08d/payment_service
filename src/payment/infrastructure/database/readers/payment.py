from uuid import UUID

from sqlalchemy import select

from payment.application.payment.dto import PaymentDetailDTO
from payment.application.payment.interfaces.persistence import PaymentReader
from payment.infrastructure.database.converters.payment import convert_db_row_to_payment_detail
from payment.infrastructure.database.models.payment import PAYMENT_TABLE

from .base import SQLAlchemyReader


class PaymentSQLAlchemyReader(SQLAlchemyReader, PaymentReader):
    async def get_payment_by_id(self, payment_id: UUID) -> PaymentDetailDTO | None:
        result = await self._session.execute(
            select(PAYMENT_TABLE).where(
                PAYMENT_TABLE.c.id == payment_id,
            )
        )
        row = result.mappings().one_or_none()
        return None if row is None else convert_db_row_to_payment_detail(row)
