"""Purchase aggregate root."""

from __future__ import annotations

from datetime import datetime, timezone

from numera.domain.shared.events import DomainEvent
from numera.domain.shared.value_objects import Money

from .events import (
    PaymentRegistered,
    PurchaseApproved,
    PurchaseCancelled,
    PurchaseCreated,
    PurchasePaid,
)
from .exceptions import InvalidPayment, InvalidPurchaseTransition
from .ids import InvoiceId, PurchaseId, SupplierId
from .status import PurchaseStatus


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Purchase:
    """Consistency boundary for a supplier purchase.

    State can only change through explicit business operations. The aggregate
    records domain events but never publishes them itself.
    """

    __slots__ = (
        "_id",
        "_supplier_id",
        "_invoice_id",
        "_total",
        "_outstanding",
        "_status",
        "_created_at",
        "_updated_at",
        "_events",
    )

    def __init__(
        self,
        *,
        purchase_id: PurchaseId,
        supplier_id: SupplierId,
        invoice_id: InvoiceId,
        total: Money,
        outstanding: Money,
        status: PurchaseStatus,
        created_at: datetime,
        updated_at: datetime,
        events: list[DomainEvent] | None = None,
    ) -> None:
        if not total.is_positive():
            raise ValueError("Purchase total must be positive.")
        if total.currency != outstanding.currency:
            raise ValueError("Total and outstanding must use the same currency.")
        if outstanding.is_negative() or outstanding > total:
            raise ValueError("Outstanding must be between zero and total.")

        self._id = purchase_id
        self._supplier_id = supplier_id
        self._invoice_id = invoice_id
        self._total = total
        self._outstanding = outstanding
        self._status = status
        self._created_at = created_at
        self._updated_at = updated_at
        self._events = list(events or [])

    @classmethod
    def create(
        cls,
        *,
        purchase_id: PurchaseId,
        supplier_id: SupplierId,
        invoice_id: InvoiceId,
        total: Money,
        occurred_at: datetime | None = None,
    ) -> Purchase:
        now = occurred_at or _utc_now()
        purchase = cls(
            purchase_id=purchase_id,
            supplier_id=supplier_id,
            invoice_id=invoice_id,
            total=total,
            outstanding=total,
            status=PurchaseStatus.RECEIVED,
            created_at=now,
            updated_at=now,
        )
        purchase._record(PurchaseCreated(purchase_id=purchase_id, total=total))
        return purchase

    @property
    def id(self) -> PurchaseId:
        return self._id

    @property
    def supplier_id(self) -> SupplierId:
        return self._supplier_id

    @property
    def invoice_id(self) -> InvoiceId:
        return self._invoice_id

    @property
    def total(self) -> Money:
        return self._total

    @property
    def outstanding(self) -> Money:
        return self._outstanding

    @property
    def status(self) -> PurchaseStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def approve(self) -> None:
        if self._status is not PurchaseStatus.RECEIVED:
            raise InvalidPurchaseTransition(
                f"Cannot approve purchase in {self._status.value} status."
            )
        self._status = PurchaseStatus.APPROVED
        self._touch()
        self._record(PurchaseApproved(purchase_id=self._id))

    def cancel(self) -> None:
        if self._status not in {PurchaseStatus.RECEIVED, PurchaseStatus.APPROVED}:
            raise InvalidPurchaseTransition(
                f"Cannot cancel purchase in {self._status.value} status."
            )
        self._status = PurchaseStatus.CANCELLED
        self._touch()
        self._record(PurchaseCancelled(purchase_id=self._id))

    def register_payment(self, amount: Money) -> None:
        if self._status not in {
            PurchaseStatus.APPROVED,
            PurchaseStatus.PARTIALLY_PAID,
        }:
            raise InvalidPurchaseTransition(
                f"Cannot register payment in {self._status.value} status."
            )
        if amount.currency != self._outstanding.currency:
            # Money subtraction would also reject this, but this message is
            # expressed in purchase-domain terms.
            raise InvalidPayment("Payment currency must match the purchase currency.")
        if not amount.is_positive():
            raise InvalidPayment("Payment amount must be positive.")
        if amount > self._outstanding:
            raise InvalidPayment("Payment cannot exceed the outstanding balance.")

        self._outstanding = self._outstanding - amount
        self._status = (
            PurchaseStatus.PAID
            if self._outstanding.is_zero()
            else PurchaseStatus.PARTIALLY_PAID
        )
        self._touch()
        self._record(
            PaymentRegistered(
                purchase_id=self._id,
                amount=amount,
                outstanding=self._outstanding,
            )
        )
        if self._status is PurchaseStatus.PAID:
            self._record(PurchasePaid(purchase_id=self._id))

    def pull_events(self) -> tuple[DomainEvent, ...]:
        """Return and clear pending events after successful persistence."""

        events = tuple(self._events)
        self._events.clear()
        return events

    def peek_events(self) -> tuple[DomainEvent, ...]:
        return tuple(self._events)

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)

    def _touch(self) -> None:
        self._updated_at = _utc_now()
