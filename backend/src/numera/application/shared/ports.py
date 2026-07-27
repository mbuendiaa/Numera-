"""Ports shared by application use cases."""

from collections.abc import Iterable
from typing import Protocol

from numera.domain.shared.events import DomainEvent


class EventPublisher(Protocol):
    """Publishes domain events after a successful application transaction."""

    def publish(self, events: Iterable[DomainEvent]) -> None:
        ...
