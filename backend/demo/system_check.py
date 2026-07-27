"""Fast smoke check for Numera's purchase runtime."""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
_SRC = _BACKEND / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from numera.application.purchase import CreatePurchaseCommand  # noqa: E402
from numera.domain.purchase import PurchaseId  # noqa: E402
from numera.domain.shared.value_objects import Currency, Money  # noqa: E402
from numera.infrastructure.wiring.container import build_container  # noqa: E402


def main() -> int:
    print("NUMERA SYSTEM CHECK")
    print("=" * 40)

    assert Money("1.00", Currency.EUR).amount == Money("1", Currency.EUR).amount
    print("[OK] Money")

    container = build_container()
    print("[OK] Application container")
    print("[OK] In-memory repository")
    print("[OK] Domain event bus")

    result = container.create_purchase.execute(
        CreatePurchaseCommand(
            purchase_id="system-check-purchase",
            supplier_id="system-check-supplier",
            invoice_id="system-check-invoice",
            total_amount="10.00",
            currency=Currency.EUR,
        )
    )
    assert container.purchase_repository.get(PurchaseId(result.purchase_id)) is not None
    assert len(container.event_bus.published_events) == 1
    print("[OK] Purchase application flow")

    print("=" * 40)
    print("ALL SYSTEMS OPERATIONAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
