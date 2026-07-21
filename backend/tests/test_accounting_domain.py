import pytest
from numera.domain.accounting.models import AccountingEvent, AccountingEventSource, AccountingEventType, JournalEntry, JournalLine


def test_accounting_event_balances():
    event = AccountingEvent(
        company_id="company_demo",
        event_type=AccountingEventType.PURCHASE_INVOICE,
        source=AccountingEventSource.DOCUMENT_ENGINE,
        event_date="2026-04-21",
        supplier_name="CONGELADOS LA RED 2000,SL",
        base_amount=309.60,
        tax_amount=30.96,
        total_amount=340.56,
    )
    assert event.total_amount == 340.56


def test_accounting_event_rejects_unbalanced_amounts():
    with pytest.raises(ValueError):
        AccountingEvent(
            company_id="company_demo",
            event_type=AccountingEventType.PURCHASE_INVOICE,
            source=AccountingEventSource.DOCUMENT_ENGINE,
            event_date="2026-04-21",
            base_amount=309.60,
            tax_amount=30.96,
            total_amount=999.99,
        )


def test_journal_entry_must_balance():
    entry = JournalEntry(
        company_id="company_demo",
        event_type=AccountingEventType.PURCHASE_INVOICE,
        entry_date="2026-04-21",
        description="Factura compra",
        lines=[
            JournalLine(account_code="600000", description="Compra", debit=309.60),
            JournalLine(account_code="472000", description="IVA", debit=30.96),
            JournalLine(account_code="400000", description="Proveedor", credit=340.56),
        ],
    )
    assert entry.is_balanced
    assert entry.total_debit == 340.56
    assert entry.total_credit == 340.56
