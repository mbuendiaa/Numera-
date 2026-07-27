"""In-memory implementation of the Purchase repository contract."""

from __future__ import annotations

from threading import RLock

from numera.domain.purchase import Purchase, PurchaseId


class InMemoryPurchaseRepository:
    """Stores purchase aggregates for the lifetime of the process.

    This adapter is useful for demos, tests and local development. It deliberately
    exposes the same contract as a future SQLAlchemy/PostgreSQL implementation.
    """

    def __init__(self) -> None:
        self._purchases: dict[PurchaseId, Purchase] = {}
        self._lock = RLock()

    def save(self, purchase: Purchase) -> None:
        with self._lock:
            self._purchases[purchase.id] = purchase

    def get(self, purchase_id: PurchaseId) -> Purchase | None:
        with self._lock:
            return self._purchases.get(purchase_id)

    def list(self) -> list[Purchase]:
        with self._lock:
            return list(self._purchases.values())

    def clear(self) -> None:
        with self._lock:
            self._purchases.clear()
