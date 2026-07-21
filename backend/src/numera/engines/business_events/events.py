from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def new_event_id() -> str:
    return f"event_{uuid4().hex[:12]}"


@dataclass(frozen=True, slots=True)
class BusinessEvent:
    company_id: str
    event_id: str = field(default_factory=new_event_id)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def event_type(self) -> str:
        return type(self).__name__

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["event_type"] = self.event_type
        payload["occurred_at"] = self.occurred_at.isoformat()
        return payload


@dataclass(frozen=True, slots=True)
class DocumentUploaded(BusinessEvent):
    document_id: str = ""
    filename: str = ""
    document_type: str = "unknown"


@dataclass(frozen=True, slots=True)
class SupplierResolved(BusinessEvent):
    supplier_id: str = ""
    supplier_name: str = ""
    created: bool = False


@dataclass(frozen=True, slots=True)
class InvoiceCreated(BusinessEvent):
    invoice_id: str = ""
    supplier_id: str | None = None
    invoice_number: str = ""
    total_amount: float = 0.0
    source_document_id: str | None = None


@dataclass(frozen=True, slots=True)
class JournalEntryProposed(BusinessEvent):
    journal_entry_id: str = ""
    source_document_id: str | None = None
    total_debit: float = 0.0
    total_credit: float = 0.0
