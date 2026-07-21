"""Base type for immutable domain events."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True, kw_only=True)
class DomainEvent:
    """Fact emitted by a domain aggregate.

    Events are created inside the domain and published by the application layer
    only after the aggregate has been persisted successfully.
    """

    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=_utc_now)
