from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Header, status

from payment.application.common.mediator import Mediator
from payment.application.payment.commands import CreatePaymentCommand
from payment.application.payment.queries import GetPaymentByIdQuery

from .schemas import CreatePaymentRequest, CreatePaymentResponse, ErrorResponse, PaymentResponse

router = APIRouter(prefix="/api/v1/payments", tags=["payments"], route_class=DishkaRoute)


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=CreatePaymentResponse,
    responses={409: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Создать платёж",
)
async def create_payment(
    body: CreatePaymentRequest,
    mediator: FromDishka[Mediator],
    idempotency_key: Annotated[
        UUID, Header(alias="Idempotency-Key", description="UUID, уникальный для каждого платежа")
    ],
) -> CreatePaymentResponse:
    result = await mediator.send(
        CreatePaymentCommand(
            idempotency_key=idempotency_key,
            amount=body.amount,
            currency=body.currency,
            description=body.description,
            webhook_url=body.webhook_url,
            metadata=body.metadata,
        )
    )

    return CreatePaymentResponse(payment_id=result.payment_id, status=result.status, created_at=result.created_at)


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Получить платёж",
)
async def get_payment(payment_id: UUID, mediator: FromDishka[Mediator]) -> PaymentResponse:
    payment = await mediator.send(GetPaymentByIdQuery(payment_id=payment_id))

    return PaymentResponse(**vars(payment))
