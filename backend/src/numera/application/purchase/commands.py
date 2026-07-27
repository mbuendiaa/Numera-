"""Commands accepted by purchase application use cases."""

from dataclasses import dataclass
from decimal import Decimal

from numera.domain.shared.value_objects import Currency


@dataclass(frozen=True, slots=True)
class CreatePurchaseCommand:
    purchase_id: str
    supplier_id: str
    invoice_id: str
    total_amount: Decimal | int | str
    currency: Currency | str


@dataclass(frozen=True, slots=True)
class ApprovePurchaseCommand:
    purchase_id: str


@dataclass(frozen=True, slots=True)
class RegisterPaymentCommand:
    purchase_id: str
    amount: Decimal | int | str
    currency: Currency | str
