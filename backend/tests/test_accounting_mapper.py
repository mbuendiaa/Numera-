from numera.domain.accounting.models import AccountingEventType
from numera.domain.accounting_mapper import AccountingEventMapper
from numera.engines.accounting.engine import AccountingEngine


class FakeInvoice:
    id = "invoice_demo"
    company_id = "company_demo"
    supplier_id = None
    invoice_number = "V1/2604047"
    issue_date = "21/04/2026"
    base_amount = 309.60
    tax_amount = 30.96
    total_amount = 340.56
    status = "received"
    source_document_id = "document_demo"


def test_invoice_maps_to_accounting_event_and_entry():
    invoice = FakeInvoice()

    event = AccountingEventMapper().from_purchase_invoice(
        invoice,
        supplier_name="CONGELADOS LA RED 2000,SL",
    )

    assert event.event_type == AccountingEventType.PURCHASE_INVOICE
    assert event.base_amount == 309.60

    entry = AccountingEngine().generate_entry(event)

    assert entry.is_balanced
    assert entry.total_debit == 340.56
    assert entry.total_credit == 340.56
