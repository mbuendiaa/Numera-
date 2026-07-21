from numera.domain.accounting.models import (
    AccountingEvent,
    AccountingEventSource,
    AccountingEventType,
)
from numera.infrastructure.persistence.models import InvoiceORM


class AccountingEventMapper:
    """Maps persisted business objects into Accounting Events.

    The Accounting Engine should not depend directly on invoices, documents,
    OCR outputs or future email/bank objects. It receives AccountingEvent.
    """

    def from_purchase_invoice(self, invoice: InvoiceORM, supplier_name: str | None = None) -> AccountingEvent:
        return AccountingEvent(
            company_id=invoice.company_id,
            event_type=AccountingEventType.PURCHASE_INVOICE,
            source=AccountingEventSource.DOCUMENT_ENGINE,
            source_document_id=invoice.source_document_id,
            supplier_id=invoice.supplier_id,
            supplier_name=supplier_name,
            event_date=invoice.issue_date,
            currency="EUR",
            description=f"Factura de compra {invoice.invoice_number}",
            base_amount=invoice.base_amount,
            tax_amount=invoice.tax_amount,
            total_amount=invoice.total_amount,
            metadata={
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "status": invoice.status,
            },
        )
