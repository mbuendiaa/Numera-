"""Read-only data returned by purchase application use cases."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from numera.domain.purchase import Purchase


@dataclass(frozen=True, slots=True)
class PurchaseDTO:
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
    def from_domain(cls, purchase: Purchase) -> "PurchaseDTO":
        return cls(
            purchase_id=str(purchase.id),
            supplier_id=str(purchase.supplier_id),
            invoice_id=str(purchase.invoice_id),
            total_amount=purchase.total.amount,
            outstanding_amount=purchase.outstanding.amount,
            currency=purchase.total.currency.value,
            status=purchase.status.value,
            created_at=purchase.created_at,
            updated_at=purchase.updated_at,
        )
