from typing import Any

from pydantic import BaseModel


class ExtractedField(BaseModel):
    value: Any
    confidence: float
    source: str


class InvoiceExtraction(BaseModel):
    supplier_name: ExtractedField | None = None
    supplier_tax_id: ExtractedField | None = None
    customer_number: ExtractedField | None = None
    invoice_number: ExtractedField | None = None
    invoice_date: ExtractedField | None = None
    due_date: ExtractedField | None = None
    payment_method: ExtractedField | None = None
    base_amount: ExtractedField | None = None
    vat_rate: ExtractedField | None = None
    tax_amount: ExtractedField | None = None
    total_amount: ExtractedField | None = None
    currency: ExtractedField | None = None
    line_items: ExtractedField | None = None
    global_confidence: float = 0.0
