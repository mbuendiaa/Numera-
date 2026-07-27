"""Composition root for the purchase application runtime."""

from __future__ import annotations

from dataclasses import dataclass

from numera.application.purchase import (
    ApprovePurchaseUseCase,
    CreatePurchaseUseCase,
    RegisterPaymentUseCase,
)
from numera.domain.purchase import (
    PaymentRegistered,
    PurchaseApproved,
    PurchaseCancelled,
    PurchaseCreated,
    PurchasePaid,
)
from numera.infrastructure.events import ConsoleEventLogger, SimpleEventBus
from numera.infrastructure.persistence.in_memory import InMemoryPurchaseRepository


@dataclass(slots=True)
class ApplicationContainer:
    purchase_repository: InMemoryPurchaseRepository
    event_bus: SimpleEventBus
    create_purchase: CreatePurchaseUseCase
    approve_purchase: ApprovePurchaseUseCase
    register_payment: RegisterPaymentUseCase


def build_container(*, log_events: bool = False) -> ApplicationContainer:
    repository = InMemoryPurchaseRepository()
    event_bus = SimpleEventBus()

    if log_events:
        logger = ConsoleEventLogger()
        for event_type in (
            PurchaseCreated,
            PurchaseApproved,
            PaymentRegistered,
            PurchasePaid,
            PurchaseCancelled,
        ):
            event_bus.subscribe(event_type, logger)

    return ApplicationContainer(
        purchase_repository=repository,
        event_bus=event_bus,
        create_purchase=CreatePurchaseUseCase(repository, event_bus),
        approve_purchase=ApprovePurchaseUseCase(repository, event_bus),
        register_payment=RegisterPaymentUseCase(repository, event_bus),
    )
