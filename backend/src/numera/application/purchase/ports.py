"""Output ports required by purchase application use cases."""

from typing import Protocol

from numera.domain.purchase import Purchase, PurchaseId


class PurchaseRepository(Protocol):
    """Persistence contract owned by the application layer."""

    def save(self, purchase: Purchase) -> None:
        ...

    def get(self, purchase_id: PurchaseId) -> Purchase | None:
        ...
