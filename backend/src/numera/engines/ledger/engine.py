from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from numera.domain.accounting.models import JournalEntry, JournalEntryStatus
from numera.infrastructure.repositories import JournalRepository


@dataclass(frozen=True)
class LedgerQuery:
    company_id: str | None = None
    status: JournalEntryStatus | None = None
    date_from: str | None = None
    date_to: str | None = None
    account_code: str | None = None


class LedgerEngine:
    """Application service responsible for journal persistence and retrieval.

    The Accounting Engine creates balanced accounting proposals. The Ledger Engine
    stores those proposals, prevents duplicate postings and controls their lifecycle.
    """

    def __init__(self, repository: JournalRepository):
        self.repository = repository

    def record(self, entry: JournalEntry):
        if not entry.is_balanced:
            raise ValueError("Only balanced journal entries can be recorded.")
        return self.repository.save(entry)

    def get(self, entry_id: str):
        return self.repository.get(entry_id)

    def list(self, query: LedgerQuery):
        return self.repository.list(
            company_id=query.company_id,
            status=query.status.value if query.status else None,
            date_from=query.date_from,
            date_to=query.date_to,
            account_code=query.account_code,
        )

    def post(self, entry_id: str):
        entry = self._required_entry(entry_id)
        if entry.status == JournalEntryStatus.REJECTED.value:
            raise ValueError("A rejected journal entry cannot be posted.")
        if not entry.is_balanced:
            raise ValueError("An unbalanced journal entry cannot be posted.")
        return self.repository.update_status(entry_id, JournalEntryStatus.POSTED.value)

    def approve(self, entry_id: str):
        entry = self._required_entry(entry_id)
        if entry.status == JournalEntryStatus.REJECTED.value:
            raise ValueError("A rejected journal entry cannot be approved.")
        return self.repository.update_status(entry_id, JournalEntryStatus.APPROVED.value)

    def reject(self, entry_id: str):
        entry = self._required_entry(entry_id)
        if entry.status == JournalEntryStatus.POSTED.value:
            raise ValueError("A posted journal entry cannot be rejected.")
        return self.repository.update_status(entry_id, JournalEntryStatus.REJECTED.value)

    def _required_entry(self, entry_id: str):
        entry = self.repository.get(entry_id)
        if entry is None:
            raise LookupError("Journal entry not found")
        return entry


def parse_ledger_date(value: str) -> datetime:
    for pattern in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, pattern)
        except ValueError:
            continue
    raise ValueError("Dates must use DD/MM/YYYY or YYYY-MM-DD format.")
