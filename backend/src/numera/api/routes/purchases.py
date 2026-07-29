"""HTTP API for the Purchase bounded context."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from numera.application.purchase import (
    ApprovePurchaseCommand,
    CreatePurchaseCommand,
    PurchaseDTO,
    PurchaseNotFoundError,
    RegisterPaymentCommand,
)
from numera.domain.purchase import (
    InvalidPayment,
    InvalidPurchaseTransition,
    PurchaseId,
)
from numera.domain.shared.value_objects import Currency
from numera.infrastructure.wiring.container import ApplicationContainer, build_container

router = APIRouter()

# The current purchase adapter is intentionally in-memory. Keeping one container
# for the process ensures purchases survive between requests during local use.
_container = build_container(log_events=False)


def get_purchase_container() -> ApplicationContainer:
    """FastAPI dependency exposed so tests or future adapters can override it."""

    return _container


class PurchaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    purchase_id: str = Field(min_length=1, examples=["purchase_001"])
    supplier_id: str = Field(min_length=1, examples=["supplier_001"])
    invoice_id: str = Field(min_length=1, examples=["invoice_001"])
    total_amount: Decimal = Field(gt=0, examples=["1250.50"])
    currency: Currency = Currency.EUR


class PaymentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(gt=0, examples=["250.00"])
    currency: Currency = Currency.EUR


class PurchaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    purchase_id: str
    supplier_id: str
    invoice_id: str
    total_amount: Decimal
    outstanding_amount: Decimal
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: PurchaseDTO) -> "PurchaseRead":
        return cls.model_validate(dto)


def _not_found(exc: PurchaseNotFoundError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


def _business_conflict(exc: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/", response_model=PurchaseRead, status_code=status.HTTP_201_CREATED)
def create_purchase(
    payload: PurchaseCreate,
    container: ApplicationContainer = Depends(get_purchase_container),
):
    existing = container.purchase_repository.get(PurchaseId(payload.purchase_id))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Purchase {payload.purchase_id} already exists.",
        )

    try:
        dto = container.create_purchase.execute(
            CreatePurchaseCommand(
                purchase_id=payload.purchase_id,
                supplier_id=payload.supplier_id,
                invoice_id=payload.invoice_id,
                total_amount=payload.total_amount,
                currency=payload.currency,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return PurchaseRead.from_dto(dto)


@router.get("/", response_model=list[PurchaseRead])
def list_purchases(
    container: ApplicationContainer = Depends(get_purchase_container),
):
    purchases = container.purchase_repository.list()
    purchases.sort(key=lambda item: item.created_at)
    return [PurchaseRead.from_dto(PurchaseDTO.from_domain(item)) for item in purchases]


@router.get("/{purchase_id}", response_model=PurchaseRead)
def get_purchase(
    purchase_id: str,
    container: ApplicationContainer = Depends(get_purchase_container),
):
    try:
        purchase = container.purchase_repository.get(PurchaseId(purchase_id))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if purchase is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase {purchase_id} was not found.",
        )
    return PurchaseRead.from_dto(PurchaseDTO.from_domain(purchase))


@router.post("/{purchase_id}/approve", response_model=PurchaseRead)
def approve_purchase(
    purchase_id: str,
    container: ApplicationContainer = Depends(get_purchase_container),
):
    try:
        dto = container.approve_purchase.execute(ApprovePurchaseCommand(purchase_id=purchase_id))
    except PurchaseNotFoundError as exc:
        raise _not_found(exc) from exc
    except (InvalidPurchaseTransition, ValueError) as exc:
        raise _business_conflict(exc) from exc
    return PurchaseRead.from_dto(dto)


@router.post("/{purchase_id}/payments", response_model=PurchaseRead)
def register_payment(
    purchase_id: str,
    payload: PaymentCreate,
    container: ApplicationContainer = Depends(get_purchase_container),
):
    try:
        dto = container.register_payment.execute(
            RegisterPaymentCommand(
                purchase_id=purchase_id,
                amount=payload.amount,
                currency=payload.currency,
            )
        )
    except PurchaseNotFoundError as exc:
        raise _not_found(exc) from exc
    except (InvalidPurchaseTransition, InvalidPayment, ValueError) as exc:
        raise _business_conflict(exc) from exc
    return PurchaseRead.from_dto(dto)
