from typing import NoReturn

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from payment.application.common.exceptions import RepositoryError
from payment.application.payment.exceptions import IdempotencyKeyAlreadyExistError
from payment.domain.payment.entities import Payment
from payment.domain.payment.repositories import PaymentRepository
from payment.domain.payment.value_objects import IdempotencyKey, PaymentID
from payment.infrastructure.database.models import PAYMENT_TABLE

from .base import SQLAlchemyRepository


class PaymentSQLAlchemyRepository(SQLAlchemyRepository, PaymentRepository):
    async def acquire_by_id(self, payment_id: PaymentID) -> Payment | None:
        return await self._session.get(
            Payment,
            payment_id.value,
            with_for_update=True,
        )

    async def acquire_by_idempotency_key(self, idempotency_key: IdempotencyKey) -> Payment:
        result = await self._session.execute(
            select(Payment)
            .where(PAYMENT_TABLE.c.idempotency_key == idempotency_key.value)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return result.scalar_one()

    async def save(self, payment: Payment) -> None:
        self._session.add(payment)
        try:
            await self._session.flush()
        except IntegrityError as err:
            self._raise_domain_error(err, payment)

    @staticmethod
    def _raise_domain_error(err: IntegrityError, payment: Payment) -> NoReturn:
        driver_error = getattr(err.orig, "__cause__", None)

        if getattr(driver_error, "constraint_name", None) == "uq_payments_idempotency_key":
            raise IdempotencyKeyAlreadyExistError(payment.idempotency_key.value) from err

        raise RepositoryError from err
