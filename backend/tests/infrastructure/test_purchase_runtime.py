from numera.application.purchase import CreatePurchaseCommand
from numera.domain.purchase import PurchaseCreated, PurchaseId
from numera.domain.shared.value_objects import Currency
from numera.infrastructure.persistence.in_memory import InMemoryPurchaseRepository
from numera.infrastructure.wiring.container import build_container


def _create_purchase(container, purchase_id: str = "purchase-1"):
    return container.create_purchase.execute(
        CreatePurchaseCommand(
            purchase_id=purchase_id,
            supplier_id="supplier-1",
            invoice_id="invoice-1",
            total_amount="25.00",
            currency=Currency.EUR,
        )
    )


def test_in_memory_repository_stores_purchase_aggregate() -> None:
    container = build_container()
    result = _create_purchase(container)

    stored = container.purchase_repository.get(PurchaseId(result.purchase_id))

    assert stored is not None
    assert container.purchase_repository.list() == [stored]


def test_event_bus_delivers_and_records_domain_event() -> None:
    container = build_container()
    received: list[PurchaseCreated] = []
    container.event_bus.subscribe(PurchaseCreated, received.append)

    _create_purchase(container)

    assert len(received) == 1
    assert tuple(received) == container.event_bus.published_events


def test_container_wires_shared_repository_across_use_cases() -> None:
    container = build_container()
    _create_purchase(container)

    approved = container.approve_purchase.execute(
        __import__(
            "numera.application.purchase",
            fromlist=["ApprovePurchaseCommand"],
        ).ApprovePurchaseCommand("purchase-1")
    )

    assert approved.status == "APPROVED"
    assert isinstance(container.purchase_repository, InMemoryPurchaseRepository)
