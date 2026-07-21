from datetime import datetime, timezone
from decimal import Decimal

import pytest

from numera.domain.purchase import (
    InvalidPayment,
    InvalidPurchaseTransition,
    InvoiceId,
    PaymentRegistered,
    Purchase,
    PurchaseApproved,
    PurchaseCancelled,
    PurchaseCreated,
    PurchaseId,
    PurchasePaid,
    PurchaseStatus,
    SupplierId,
)
from numera.domain.shared.value_objects import Currency, Money


def make_purchase(total: str = "100.00") -> Purchase:
    return Purchase.create(
        purchase_id=PurchaseId("purchase_1"),
        supplier_id=SupplierId("supplier_1"),
        invoice_id=InvoiceId("invoice_1"),
        total=Money(Decimal(total), Currency.EUR),
        occurred_at=datetime(2026, 7, 21, tzinfo=timezone.utc),
    )


def test_purchase_is_created_received_with_full_balance():
    purchase = make_purchase()

    assert purchase.status is PurchaseStatus.RECEIVED
    assert purchase.outstanding == purchase.total
    assert purchase.created_at == datetime(2026, 7, 21, tzinfo=timezone.utc)
    assert isinstance(purchase.peek_events()[0], PurchaseCreated)


def test_purchase_requires_positive_total():
    with pytest.raises(ValueError, match="positive"):
        make_purchase("0.00")


def test_approve_changes_status_and_records_event():
    purchase = make_purchase()
    purchase.pull_events()

    purchase.approve()

    assert purchase.status is PurchaseStatus.APPROVED
    assert isinstance(purchase.peek_events()[0], PurchaseApproved)


def test_purchase_cannot_be_approved_twice():
    purchase = make_purchase()
    purchase.approve()

    with pytest.raises(InvalidPurchaseTransition):
        purchase.approve()


def test_received_purchase_can_be_cancelled():
    purchase = make_purchase()
    purchase.pull_events()

    purchase.cancel()

    assert purchase.status is PurchaseStatus.CANCELLED
    assert isinstance(purchase.peek_events()[0], PurchaseCancelled)


def test_cancelled_purchase_cannot_be_approved():
    purchase = make_purchase()
    purchase.cancel()

    with pytest.raises(InvalidPurchaseTransition):
        purchase.approve()


def test_payment_requires_approved_purchase():
    purchase = make_purchase()

    with pytest.raises(InvalidPurchaseTransition):
        purchase.register_payment(Money(Decimal("10.00"), Currency.EUR))


def test_partial_payment_updates_balance_and_status():
    purchase = make_purchase()
    purchase.approve()
    purchase.pull_events()

    purchase.register_payment(Money(Decimal("40.00"), Currency.EUR))

    assert purchase.outstanding == Money(Decimal("60.00"), Currency.EUR)
    assert purchase.status is PurchaseStatus.PARTIALLY_PAID
    events = purchase.peek_events()
    assert len(events) == 1
    assert isinstance(events[0], PaymentRegistered)
    assert events[0].outstanding == Money(Decimal("60.00"), Currency.EUR)


def test_full_payment_marks_purchase_paid_and_records_both_events():
    purchase = make_purchase()
    purchase.approve()
    purchase.pull_events()

    purchase.register_payment(Money(Decimal("100.00"), Currency.EUR))

    assert purchase.outstanding == Money.zero(Currency.EUR)
    assert purchase.status is PurchaseStatus.PAID
    assert [type(event) for event in purchase.peek_events()] == [
        PaymentRegistered,
        PurchasePaid,
    ]


def test_second_payment_can_complete_partially_paid_purchase():
    purchase = make_purchase()
    purchase.approve()
    purchase.register_payment(Money(Decimal("25.00"), Currency.EUR))
    purchase.pull_events()

    purchase.register_payment(Money(Decimal("75.00"), Currency.EUR))

    assert purchase.status is PurchaseStatus.PAID
    assert purchase.outstanding.is_zero()


def test_payment_must_be_positive():
    purchase = make_purchase()
    purchase.approve()

    with pytest.raises(InvalidPayment, match="positive"):
        purchase.register_payment(Money.zero(Currency.EUR))


def test_payment_cannot_exceed_outstanding():
    purchase = make_purchase()
    purchase.approve()

    with pytest.raises(InvalidPayment, match="exceed"):
        purchase.register_payment(Money(Decimal("100.01"), Currency.EUR))


def test_payment_currency_must_match_purchase():
    purchase = make_purchase()
    purchase.approve()

    with pytest.raises(InvalidPayment, match="currency"):
        purchase.register_payment(Money(Decimal("10.00"), Currency.USD))


def test_paid_purchase_cannot_be_cancelled():
    purchase = make_purchase()
    purchase.approve()
    purchase.register_payment(Money(Decimal("100.00"), Currency.EUR))

    with pytest.raises(InvalidPurchaseTransition):
        purchase.cancel()


def test_partially_paid_purchase_cannot_be_cancelled():
    purchase = make_purchase()
    purchase.approve()
    purchase.register_payment(Money(Decimal("10.00"), Currency.EUR))

    with pytest.raises(InvalidPurchaseTransition):
        purchase.cancel()


def test_pull_events_returns_and_clears_pending_events():
    purchase = make_purchase()

    events = purchase.pull_events()

    assert len(events) == 1
    assert isinstance(events[0], PurchaseCreated)
    assert purchase.peek_events() == ()


def test_typed_ids_reject_empty_values():
    with pytest.raises(ValueError):
        PurchaseId("   ")
