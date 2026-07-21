"""Typed identifiers used by the Purchase bounded context."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EntityId:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip() if isinstance(self.value, str) else ""
        if not normalized:
            raise ValueError(f"{type(self).__name__} cannot be empty.")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class PurchaseId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class SupplierId(EntityId):
    pass


@dataclass(frozen=True, slots=True)
class InvoiceId(EntityId):
    pass
