"""Business scenario: supplier invoice received, approved and fully paid."""

from __future__ import annotations

import json
from pathlib import Path

from numera.domain.purchase import (
    InvoiceId,
    PaymentRegistered,
    Purchase,
    PurchaseApproved,
    PurchaseCreated,
    PurchaseId,
    PurchasePaid,
    PurchaseStatus,
    SupplierId,
)
from numera.domain.shared.value_objects import Currency, Money

_FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict[str, str]:
    with (_FIXTURES / name).open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def test_amazon_invoice_purchase_flow() -> None:
    supplier = _load_fixture("supplier_amazon.json")
    invoice = _load_fixture("invoice_amazon.json")
    total = Money(invoice["total_amount"], Currency(invoice["currency"]))

    purchase = Purchase.create(
        purchase_id=PurchaseId("purchase-amazon-2026-001"),
        supplier_id=SupplierId(supplier["supplier_id"]),
        invoice_id=InvoiceId(invoice["invoice_id"]),
        total=total,
    )

    assert purchase.status is PurchaseStatus.RECEIVED
    assert purchase.total == Money("1210.00", Currency.EUR)
    assert purchase.outstanding == purchase.total

    purchase.approve()
    purchase.register_payment(Money("210.00", Currency.EUR))

    assert purchase.status is PurchaseStatus.PARTIALLY_PAID
    assert purchase.outstanding == Money("1000.00", Currency.EUR)

    purchase.register_payment(Money("1000.00", Currency.EUR))

    assert purchase.status is PurchaseStatus.PAID
    assert purchase.outstanding == Money.zero(Currency.EUR)

    events = purchase.pull_events()
    assert [type(event) for event in events] == [
        PurchaseCreated,
        PurchaseApproved,
        PaymentRegistered,
        PaymentRegistered,
        PurchasePaid,
    ]
    assert purchase.peek_events() == ()
