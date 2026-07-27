"""Run Numera's purchase flow through the application and infrastructure layers."""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
_SRC = _BACKEND / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from numera.application.purchase import (  # noqa: E402
    ApprovePurchaseCommand,
    CreatePurchaseCommand,
    RegisterPaymentCommand,
)
from numera.domain.shared.value_objects import Currency  # noqa: E402
from numera.infrastructure.wiring.container import build_container  # noqa: E402


def main() -> int:
    container = build_container(log_events=True)
    purchase_id = "purchase-amazon-2026-001"

    print("NUMERA PURCHASE DEMO")
    print("=" * 40)
    print("[OK] Supplier resolved: Amazon Spain")

    purchase = container.create_purchase.execute(
        CreatePurchaseCommand(
            purchase_id=purchase_id,
            supplier_id="supplier-amazon-es",
            invoice_id="invoice-amazon-2026-001",
            total_amount="1210.00",
            currency=Currency.EUR,
        )
    )
    print(f"[OK] Purchase created: {purchase.purchase_id}")

    purchase = container.approve_purchase.execute(ApprovePurchaseCommand(purchase_id))
    print(f"[OK] Purchase approved: {purchase.status.value}")

    purchase = container.register_payment.execute(
        RegisterPaymentCommand(purchase_id, "210.00", Currency.EUR)
    )
    print(f"[OK] Partial payment: outstanding {purchase.outstanding}")

    purchase = container.register_payment.execute(
        RegisterPaymentCommand(purchase_id, "1000.00", Currency.EUR)
    )
    print(f"[OK] Final payment: outstanding {purchase.outstanding}")
    print(f"[OK] Purchase status: {purchase.status.value}")
    print(f"[OK] Domain events published: {len(container.event_bus.published_events)}")
    print("=" * 40)
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
