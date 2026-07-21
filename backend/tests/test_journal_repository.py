from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from numera.domain.accounting.models import (
    AccountingEventType,
    JournalEntry,
    JournalLine,
)
from numera.infrastructure.database.base import Base
from numera.infrastructure.persistence.models import CompanyORM
from numera.infrastructure.repositories import JournalRepository


def _session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(CompanyORM(id="company_demo", name="Demo"))
    session.commit()
    return session


def _entry():
    return JournalEntry(
        company_id="company_demo",
        event_type=AccountingEventType.PURCHASE_INVOICE,
        source_document_id="document_demo",
        entry_date="21/04/2026",
        description="Factura de compra V1/2604047",
        lines=[
            JournalLine(account_code="600000", description="Compra", debit=309.60),
            JournalLine(account_code="472000", description="IVA", debit=30.96),
            JournalLine(account_code="400000", description="Proveedor", credit=340.56),
        ],
    )


def test_save_and_read_journal_entry():
    db = _session()
    saved, created = JournalRepository(db).save(_entry())

    assert created is True
    assert saved.id.startswith("journal_")
    assert len(saved.lines) == 3
    assert saved.total_debit == 340.56
    assert saved.total_credit == 340.56
    assert saved.is_balanced is True
    assert JournalRepository(db).get(saved.id).description == saved.description


def test_source_document_is_idempotent():
    db = _session()
    first, first_created = JournalRepository(db).save(_entry())
    second, second_created = JournalRepository(db).save(_entry())

    assert first_created is True
    assert second_created is False
    assert second.id == first.id
    assert len(JournalRepository(db).list("company_demo")) == 1
