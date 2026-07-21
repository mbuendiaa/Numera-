from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Callable
from threading import RLock
from typing import TypeVar

from numera.engines.business_events.events import BusinessEvent

EventT = TypeVar("EventT", bound=BusinessEvent)
EventHandler = Callable[[EventT], None]


class EventBus:
    """Small synchronous event bus with bounded history.

    Handlers run in registration order. Exceptions are propagated so a failed
    business reaction is visible to the caller instead of being silently lost.
    """

    def __init__(self, *, history_limit: int = 200):
        if history_limit < 1:
            raise ValueError("history_limit must be at least 1")
        self._handlers: dict[type[BusinessEvent], list[Callable]] = defaultdict(list)
        self._history: deque[BusinessEvent] = deque(maxlen=history_limit)
        self._lock = RLock()

    def subscribe(self, event_type: type[EventT], handler: EventHandler[EventT]) -> Callable[[], None]:
        with self._lock:
            self._handlers[event_type].append(handler)

        def unsubscribe() -> None:
            with self._lock:
                handlers = self._handlers.get(event_type, [])
                if handler in handlers:
                    handlers.remove(handler)

        return unsubscribe

    def publish(self, event: EventT) -> EventT:
        with self._lock:
            handlers = list(self._handlers.get(type(event), []))
            self._history.append(event)

        for handler in handlers:
            handler(event)
        return event

    def recent(self, *, event_type: str | None = None, company_id: str | None = None, limit: int = 50) -> list[BusinessEvent]:
        if limit < 1 or limit > 200:
            raise ValueError("limit must be between 1 and 200")
        with self._lock:
            events = list(self._history)

        if event_type:
            events = [event for event in events if event.event_type == event_type]
        if company_id:
            events = [event for event in events if event.company_id == company_id]
        return list(reversed(events[-limit:]))

    def clear(self) -> None:
        with self._lock:
            self._history.clear()


event_bus = EventBus()
