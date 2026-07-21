import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from numera.domain.accounting.models import (
    AccountingEventType,
    JournalEntry,
    JournalEntryStatus,
    JournalLine,
)
from numera.engines.ledger.engine import LedgerEngine, LedgerQuery
from numera.infrastructure.database.base import Base
from numera.infrastructure.persistence.models import CompanyORM
from numera.infrastructure.repositories import JournalRepository


def _ledger():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()
    db.add(CompanyORM(id="company_demo", name="Demo"))
    db.commit()
    return LedgerEngine(JournalRepository(db))


def _entry(document_id="document_demo", date="21/04/2026"):
    return JournalEntry(
        company_id="company_demo",
        event_type=AccountingEventType.PURCHASE_INVOICE,
        source_document_id=document_id,
        entry_date=date,
        description="Factura de compra",
        lines=[
            JournalLine(account_code="600000", description="Compra", debit=100),
            JournalLine(account_code="472000", description="IVA", debit=21),
            JournalLine(account_code="400000", description="Proveedor", credit=121),
        ],
    )


def test_ledger_records_proposal_and_prevents_duplicates():
    ledger = _ledger()
    first, created = ledger.record(_entry())
    second, created_again = ledger.record(_entry())

    assert created is True
    assert created_again is False
    assert second.id == first.id
    assert first.status == "proposed"


def test_ledger_filters_by_date_status_and_account():
    ledger = _ledger()
    first, _ = ledger.record(_entry("doc_1", "21/04/2026"))
    ledger.record(_entry("doc_2", "05/05/2026"))
    ledger.post(first.id)

    entries = ledger.list(
        LedgerQuery(
            company_id="company_demo",
            status=JournalEntryStatus.POSTED,
            date_from="2026-04-01",
            date_to="30/04/2026",
            account_code="600000",
        )
    )
    assert [entry.id for entry in entries] == [first.id]


def test_posted_entry_cannot_be_rejected():
    ledger = _ledger()
    entry, _ = ledger.record(_entry())
    ledger.post(entry.id)

    with pytest.raises(ValueError, match="cannot be rejected"):
        ledger.reject(entry.id)
