"""Console subscriber useful while running local demos."""

from numera.domain.shared.events import DomainEvent


class ConsoleEventLogger:
    def __call__(self, event: DomainEvent) -> None:
        print(f"[EVENT] {type(event).__name__} id={event.event_id}")
