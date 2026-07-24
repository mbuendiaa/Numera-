"""Run Numera's first executable business demonstration."""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
_SRC = _BACKEND / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from numera.domain.purchase import (  # noqa: E402
    InvoiceId,
    Purchase,
    PurchaseId,
    SupplierId,
)
from numera.domain.shared.value_objects import Currency, Money  # noqa: E402


def main() -> int:
    purchase = Purchase.create(
        purchase_id=PurchaseId("purchase-amazon-2026-001"),
        supplier_id=SupplierId("supplier-amazon-es"),
        invoice_id=InvoiceId("invoice-amazon-2026-001"),
        total=Money("1210.00", Currency.EUR),
    )

    print("NUMERA PURCHASE DEMO")
    print("=" * 40)
    print("[OK] Supplier resolved: Amazon Spain")
    print(f"[OK] Purchase created: {purchase.id}")

    purchase.approve()
    print(f"[OK] Purchase approved: {purchase.status.value}")

    purchase.register_payment(Money("210.00", Currency.EUR))
    print(f"[OK] Partial payment: outstanding {purchase.outstanding}")

    purchase.register_payment(Money("1000.00", Currency.EUR))
    events = purchase.pull_events()
    print(f"[OK] Final payment: outstanding {purchase.outstanding}")
    print(f"[OK] Purchase status: {purchase.status.value}")
    print(f"[OK] Domain events recorded: {len(events)}")
    print("=" * 40)
    print("SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
