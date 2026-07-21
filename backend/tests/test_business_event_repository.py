from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from numera.engines.business_events import DocumentUploaded, InvoiceCreated
from numera.infrastructure.database.base import Base
from numera.infrastructure.persistence.models import CompanyORM
from numera.infrastructure.repositories import BusinessEventRepository


def make_repository():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add(CompanyORM(id="company_1", name="Demo"))
    session.commit()
    return BusinessEventRepository(session)


def test_business_events_are_persisted_and_filterable():
    repository = make_repository()
    document_event = DocumentUploaded(
        company_id="company_1",
        document_id="document_1",
        filename="invoice.pdf",
        document_type="invoice",
    )
    invoice_event = InvoiceCreated(
        company_id="company_1",
        invoice_id="invoice_1",
        invoice_number="F-1",
        total_amount=100.0,
        source_document_id="document_1",
    )

    repository.append(document_event)
    repository.append(invoice_event)

    assert [item.event_type for item in repository.list(company_id="company_1")] == [
        "InvoiceCreated",
        "DocumentUploaded",
    ]
    assert repository.list(entity_type="invoice", entity_id="invoice_1")[0].event_id == invoice_event.event_id
    assert repository.list(entity_type="document", entity_id="document_1")[0].event_id == document_event.event_id


def test_append_is_idempotent_by_event_id():
    repository = make_repository()
    event = DocumentUploaded(company_id="company_1", document_id="document_1")

    first = repository.append(event)
    second = repository.append(event)

    assert first.event_id == second.event_id
    assert len(repository.list()) == 1
