import json

from sqlalchemy.orm import Session

from numera.domain.accounting_mapper import AccountingEventMapper
from numera.domain.schemas import InvoiceCreate
from numera.engines.accounting.engine import AccountingEngine
from numera.engines.chart_of_accounts.engine import ChartOfAccountsEngine
from numera.engines.document.pipeline import DocumentPipeline
from numera.engines.ledger.engine import LedgerEngine
from numera.infrastructure.repositories import (
    AccountRepository,
    DocumentRepository,
    InvoiceRepository,
    JournalRepository,
    SupplierRepository,
)


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.documents = DocumentRepository(db)
        self.invoices = InvoiceRepository(db)
        self.suppliers = SupplierRepository(db)
        self.ledger = LedgerEngine(JournalRepository(db))
        self.pipeline = DocumentPipeline()
        self.accounting_mapper = AccountingEventMapper()
        self.accounting_engine = AccountingEngine(ChartOfAccountsEngine(AccountRepository(db)))

    def upload_and_process(self, *, company_id: str, file):
        result = self.pipeline.run(company_id=company_id, file=file)

        document = self.documents.create(
            company_id=company_id,
            filename=file.filename,
            content_type=file.content_type or "unknown",
            storage_path=result["storage_path"],
            document_type=result["document_type"],
            status="processed",
            extracted_text_preview=result["text_preview"],
            extracted_fields_json=json.dumps(result["extracted_fields"], ensure_ascii=False),
        )

        created_invoice = None
        proposed_journal_entry = None

        if result["document_type"] == "invoice":
            created_invoice = self._try_create_invoice(
                company_id=company_id,
                document_id=document.id,
                extracted_fields=result["extracted_fields"],
            )

            if created_invoice:
                document = self.documents.set_created_invoice(document.id, created_invoice.id)

                supplier_name = self._field_value(result["extracted_fields"], "supplier_name")
                event = self.accounting_mapper.from_purchase_invoice(
                    created_invoice,
                    supplier_name=supplier_name,
                )
                generated_entry = self.accounting_engine.generate_entry(event)
                proposed_journal_entry, _ = self.ledger.record(generated_entry)

        return document, result, created_invoice, proposed_journal_entry

    def _try_create_invoice(self, *, company_id: str, document_id: str, extracted_fields: dict):
        total = self._field_value(extracted_fields, "total_amount")
        base = self._field_value(extracted_fields, "base_amount")
        tax = self._field_value(extracted_fields, "tax_amount")

        if total is None:
            return None

        supplier_name = self._field_value(extracted_fields, "supplier_name") or "Unknown Supplier"
        supplier = self.suppliers.find_by_name(company_id, supplier_name)
        supplier_id = supplier.id if supplier else None

        invoice_number = self._field_value(extracted_fields, "invoice_number") or f"AUTO-{document_id[-6:]}"
        invoice_date = self._field_value(extracted_fields, "invoice_date") or "unknown"

        payload = InvoiceCreate(
            company_id=company_id,
            supplier_id=supplier_id,
            invoice_number=str(invoice_number),
            issue_date=str(invoice_date),
            base_amount=float(base) if base is not None else 0.0,
            tax_amount=float(tax) if tax is not None else 0.0,
            total_amount=float(total),
        )

        return self.invoices.create(payload, source_document_id=document_id)

    def _field_value(self, extracted_fields: dict, field_name: str):
        field = extracted_fields.get(field_name)
        if not field:
            return None
        return field.get("value")
