"""Repository contract owned by the Purchase domain."""

from typing import Protocol

from .aggregate import Purchase
from .ids import PurchaseId


class PurchaseRepository(Protocol):
    def save(self, purchase: Purchase) -> None:
        ...

    def get(self, purchase_id: PurchaseId) -> Purchase | None:
        ...

    def list(self) -> list[Purchase]:
        ...
