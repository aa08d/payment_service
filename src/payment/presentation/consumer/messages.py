from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PaymentMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    payment_id: UUID
