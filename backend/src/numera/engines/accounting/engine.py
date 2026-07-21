from numera.domain.accounting.models import AccountingEvent, AccountingEventType, JournalEntry, JournalLine
from numera.engines.accounting.chart import ChartOfAccounts


class AccountingEngine:
    def __init__(self, chart: ChartOfAccounts | None = None):
        self.chart = chart or ChartOfAccounts()

    def generate_entry(self, event: AccountingEvent) -> JournalEntry:
        if event.event_type == AccountingEventType.PURCHASE_INVOICE:
            return self._purchase_invoice_entry(event)
        raise NotImplementedError(f"Unsupported accounting event type: {event.event_type}")

    def _purchase_invoice_entry(self, event: AccountingEvent) -> JournalEntry:
        purchase = self.chart.get("600000")
        vat = self.chart.get("472000")
        supplier = self.chart.get("400000")
        supplier_label = event.supplier_name or "Proveedor"

        return JournalEntry(
            company_id=event.company_id,
            event_type=event.event_type,
            source_document_id=event.source_document_id,
            entry_date=event.event_date,
            description=event.description or f"Factura de compra - {supplier_label}",
            lines=[
                JournalLine(account_code=purchase.code, account_name=purchase.name, description=f"Compra - {supplier_label}", debit=round(event.base_amount, 2)),
                JournalLine(account_code=vat.code, account_name=vat.name, description=f"IVA soportado - {supplier_label}", debit=round(event.tax_amount, 2)),
                JournalLine(account_code=supplier.code, account_name=supplier.name, description=f"Proveedor - {supplier_label}", credit=round(event.total_amount, 2)),
            ],
        )
