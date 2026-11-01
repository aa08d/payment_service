from typing import ClassVar
from uuid import UUID

from payment.application.common.exceptions import ApplicationError


class PaymentNotExistsError(ApplicationError):
    status: ClassVar[int] = 404

    def __init__(self, payment_id: UUID) -> None:
        self._payment_id = payment_id

    @property
    def message(self) -> str:
        return f"Payment with ID {self._payment_id} does not exist."
