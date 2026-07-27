"""Tests for the purchase application layer."""

from collections.abc import Iterable
from decimal import Decimal

import pytest

from numera.application.purchase import (
    ApprovePurchaseCommand,
    ApprovePurchaseUseCase,
    CreatePurchaseCommand,
    CreatePurchaseUseCase,
    PurchaseNotFoundError,
    RegisterPaymentCommand,
    RegisterPaymentUseCase,
)
from numera.domain.purchase import Purchase, PurchaseId
from numera.domain.shared.events import DomainEvent


class InMemoryPurchaseRepository:
    def __init__(self) -> None:
        self._purchases: dict[PurchaseId, Purchase] = {}

    def save(self, purchase: Purchase) -> None:
        self._purchases[purchase.id] = purchase

    def get(self, purchase_id: PurchaseId) -> Purchase | None:
        return self._purchases.get(purchase_id)

    def list(self) -> list[Purchase]:
        return list(self._purchases.values())


class RecordingEventPublisher:
    def __init__(self) -> None:
        self.events: list[DomainEvent] = []

    def publish(self, events: Iterable[DomainEvent]) -> None:
        self.events.extend(events)


def test_purchase_application_flow() -> None:
    repository = InMemoryPurchaseRepository()
    publisher = RecordingEventPublisher()

    created = CreatePurchaseUseCase(repository, publisher).execute(
        CreatePurchaseCommand(
            purchase_id="purchase-001",
            supplier_id="supplier-amazon-es",
            invoice_id="invoice-001",
            total_amount="1210.00",
            currency="EUR",
        )
    )
    approved = ApprovePurchaseUseCase(repository, publisher).execute(
        ApprovePurchaseCommand(purchase_id=created.purchase_id)
    )
    partially_paid = RegisterPaymentUseCase(repository, publisher).execute(
        RegisterPaymentCommand(
            purchase_id=created.purchase_id,
            amount="210.00",
            currency="EUR",
        )
    )
    paid = RegisterPaymentUseCase(repository, publisher).execute(
        RegisterPaymentCommand(
            purchase_id=created.purchase_id,
            amount="1000.00",
            currency="EUR",
        )
    )

    assert created.status == "received"
    assert approved.status == "approved"
    assert partially_paid.status == "partially_paid"
    assert partially_paid.outstanding_amount == Decimal("1000.00")
    assert paid.status == "paid"
    assert paid.outstanding_amount == Decimal("0.00")
    assert [type(event).__name__ for event in publisher.events] == [
        "PurchaseCreated",
        "PurchaseApproved",
        "PaymentRegistered",
        "PaymentRegistered",
        "PurchasePaid",
    ]


def test_approve_missing_purchase_raises_application_error() -> None:
    repository = InMemoryPurchaseRepository()
    publisher = RecordingEventPublisher()

    with pytest.raises(PurchaseNotFoundError, match="missing"):
        ApprovePurchaseUseCase(repository, publisher).execute(
            ApprovePurchaseCommand(purchase_id="missing")
        )
