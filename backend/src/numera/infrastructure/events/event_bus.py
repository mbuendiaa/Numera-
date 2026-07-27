"""Small synchronous event bus for domain events."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from threading import RLock
from typing import TypeVar

from numera.domain.shared.events import DomainEvent

EventT = TypeVar("EventT", bound=DomainEvent)
EventHandler = Callable[[EventT], None]


class SimpleEventBus:
    """Publishes domain events to handlers registered for their exact type."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[Callable[[DomainEvent], None]]] = defaultdict(list)
        self._published: list[DomainEvent] = []
        self._lock = RLock()

    def subscribe(
        self,
        event_type: type[EventT],
        handler: EventHandler[EventT],
    ) -> Callable[[], None]:
        with self._lock:
            self._handlers[event_type].append(handler)  # type: ignore[arg-type]

        def unsubscribe() -> None:
            with self._lock:
                handlers = self._handlers.get(event_type, [])
                if handler in handlers:
                    handlers.remove(handler)  # type: ignore[arg-type]

        return unsubscribe

    def publish(self, events: Iterable[DomainEvent]) -> None:
        for event in events:
            with self._lock:
                handlers = list(self._handlers.get(type(event), []))
                self._published.append(event)
            for handler in handlers:
                handler(event)

    @property
    def published_events(self) -> tuple[DomainEvent, ...]:
        with self._lock:
            return tuple(self._published)

    def clear(self) -> None:
        with self._lock:
            self._published.clear()
