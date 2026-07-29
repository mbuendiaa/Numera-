from pydantic import BaseModel, Field


class ClassificationRead(BaseModel):
    account_code: str
    confidence: float = Field(ge=0, le=1)
    reason: str
    matched_value: str | None = None


class ReviewItemRead(BaseModel):
    id: str
    item_type: str
    reason: str
    confidence: float | None = None
    status: str
    created_at: str | None = None
    reference: str | None = None


class ReviewCenterRead(BaseModel):
    company_id: str
    total_pending: int
    low_confidence: int
    ocr_errors: int
    accounting_errors: int
    duplicate_candidates: int
    items: list[ReviewItemRead]


class DashboardRead(BaseModel):
    company_id: str
    documents_processed: int
    pending_review: int
    proposed_entries: int
    approved_entries: int
    posted_entries: int
    purchase_volume_month: float
    vat_supported_month: float
    suppliers: int
    products: int
    price_alerts: int
    latest_documents: list[dict]


class SupplierAnalyticsRead(BaseModel):
    supplier_id: str
    supplier_name: str
    invoice_count: int
    total_purchased: float
    average_invoice: float
    products_supplied: int
    latest_invoice_date: str | None
    latest_purchase_price: float | None


class ProductAnalyticsRead(BaseModel):
    product_id: str
    product_name: str
    observations: int
    average_price: float | None
    latest_price: float | None
    latest_purchase_date: str | None
    best_supplier: dict | None
    worst_supplier: dict | None
    purchase_frequency_days: float | None
