from numera.domain.accounting.models import AccountingEvent, AccountingEventSource, AccountingEventType
from numera.engines.accounting.engine import AccountingEngine


def test_purchase_invoice_generates_journal_entry():
    event = AccountingEvent(
        company_id="company_demo",
        event_type=AccountingEventType.PURCHASE_INVOICE,
        source=AccountingEventSource.DOCUMENT_ENGINE,
        source_document_id="document_demo",
        event_date="2026-04-21",
        supplier_name="CONGELADOS LA RED 2000,SL",
        base_amount=309.60,
        tax_amount=30.96,
        total_amount=340.56,
    )

    entry = AccountingEngine().generate_entry(event)

    assert entry.is_balanced
    assert entry.total_debit == 340.56
    assert entry.total_credit == 340.56
    assert len(entry.lines) == 3
    assert entry.lines[0].account_code == "600000"
    assert entry.lines[1].account_code == "472000"
    assert entry.lines[2].account_code == "400000"
