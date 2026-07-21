"""Domain events emitted by the Purchase aggregate."""

from dataclasses import dataclass

from numera.domain.shared.events import DomainEvent
from numera.domain.shared.value_objects import Money

from .ids import PurchaseId


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseCreated(DomainEvent):
    purchase_id: PurchaseId
    total: Money


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseApproved(DomainEvent):
    purchase_id: PurchaseId


@dataclass(frozen=True, slots=True, kw_only=True)
class PaymentRegistered(DomainEvent):
    purchase_id: PurchaseId
    amount: Money
    outstanding: Money


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchasePaid(DomainEvent):
    purchase_id: PurchaseId


@dataclass(frozen=True, slots=True, kw_only=True)
class PurchaseCancelled(DomainEvent):
    purchase_id: PurchaseId
