"""Application services coordinating purchase domain operations."""

from numera.application.shared import EventPublisher
from numera.domain.purchase import (
    InvoiceId,
    Purchase,
    PurchaseId,
    PurchaseRepository,
    SupplierId,
)
from numera.domain.shared.value_objects import Money

from .commands import (
    ApprovePurchaseCommand,
    CreatePurchaseCommand,
    RegisterPaymentCommand,
)
from .dto import PurchaseDTO
from .exceptions import PurchaseNotFoundError


class CreatePurchaseUseCase:
    def __init__(
        self,
        repository: PurchaseRepository,
        publisher: EventPublisher,
    ) -> None:
        self._repository = repository
        self._publisher = publisher

    def execute(self, command: CreatePurchaseCommand) -> PurchaseDTO:
        purchase = Purchase.create(
            purchase_id=PurchaseId(command.purchase_id),
            supplier_id=SupplierId(command.supplier_id),
            invoice_id=InvoiceId(command.invoice_id),
            total=Money(command.total_amount, command.currency),
        )
        self._save_and_publish(purchase)
        return PurchaseDTO.from_domain(purchase)

    def _save_and_publish(self, purchase: Purchase) -> None:
        self._repository.save(purchase)
        self._publisher.publish(purchase.pull_events())


class ApprovePurchaseUseCase:
    def __init__(
        self,
        repository: PurchaseRepository,
        publisher: EventPublisher,
    ) -> None:
        self._repository = repository
        self._publisher = publisher

    def execute(self, command: ApprovePurchaseCommand) -> PurchaseDTO:
        purchase = _get_purchase(self._repository, command.purchase_id)
        purchase.approve()
        self._repository.save(purchase)
        self._publisher.publish(purchase.pull_events())
        return PurchaseDTO.from_domain(purchase)


class RegisterPaymentUseCase:
    def __init__(
        self,
        repository: PurchaseRepository,
        publisher: EventPublisher,
    ) -> None:
        self._repository = repository
        self._publisher = publisher

    def execute(self, command: RegisterPaymentCommand) -> PurchaseDTO:
        purchase = _get_purchase(self._repository, command.purchase_id)
        purchase.register_payment(Money(command.amount, command.currency))
        self._repository.save(purchase)
        self._publisher.publish(purchase.pull_events())
        return PurchaseDTO.from_domain(purchase)


def _get_purchase(
    repository: PurchaseRepository,
    raw_purchase_id: str,
) -> Purchase:
    purchase_id = PurchaseId(raw_purchase_id)
    purchase = repository.get(purchase_id)
    if purchase is None:
        raise PurchaseNotFoundError(f"Purchase {purchase_id} was not found.")
    return purchase
