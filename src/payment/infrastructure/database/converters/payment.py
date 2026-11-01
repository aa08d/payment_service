from typing import Any

from payment.application.payment.dto import PaymentDetailDTO


def convert_db_row_to_payment_detail(payment: Any) -> PaymentDetailDTO:
    return PaymentDetailDTO(
        payment_id=payment.id,
        idempotency_key=payment.idempotency_key,
        amount=payment.amount,
        currency=payment.currency,
        description=payment.description,
        webhook_url=payment.webhook_url,
        status=payment.status,
        created_at=payment.created_at,
        processed_at=payment.processed_at,
        metadata=payment.metadata,
    )
