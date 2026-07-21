from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    name: str
    country: str = "ES"
    currency: str = "EUR"


class CompanyRead(CompanyCreate):
    id: str
    model_config = {"from_attributes": True}


class SupplierCreate(BaseModel):
    company_id: str
    name: str
    tax_id: str | None = None
    country: str = "ES"
    default_account: str | None = None


class SupplierResolveRequest(BaseModel):
    company_id: str
    name: str = Field(..., min_length=1)


class SupplierRead(SupplierCreate):
    id: str
    model_config = {"from_attributes": True}


class InvoiceCreate(BaseModel):
    company_id: str
    supplier_id: str | None = None
    invoice_number: str
    issue_date: str
    base_amount: float
    tax_amount: float
    total_amount: float


class InvoiceRead(InvoiceCreate):
    id: str
    status: str
    source_document_id: str | None = None
    model_config = {"from_attributes": True}


class CognitiveDecisionRequest(BaseModel):
    company_id: str
    input_type: str = Field(..., examples=["invoice", "payment"])
    description: str
    risk_level: str = Field(default="low", examples=["low", "medium", "high"])


class CognitiveDecisionRead(BaseModel):
    id: str
    company_id: str
    input_type: str
    description: str
    risk_level: str
    status: str
    recommendation: str
    confidence: float
    explanation: str
    model_config = {"from_attributes": True}


class DocumentRead(BaseModel):
    id: str
    company_id: str
    filename: str
    content_type: str
    storage_path: str
    document_type: str
    status: str
    extracted_text_preview: str
    extracted_fields_json: str
    created_invoice_id: str | None = None
    model_config = {"from_attributes": True}


class JournalLineRead(BaseModel):
    id: str | None = None
    position: int | None = None
    account_code: str
    account_name: str | None = None
    description: str
    debit: float = 0.0
    credit: float = 0.0


class JournalEntryRead(BaseModel):
    id: str | None = None
    company_id: str
    event_type: str
    source_event_id: str | None = None
    source_document_id: str | None = None
    entry_date: str
    description: str
    status: str
    lines: list[JournalLineRead]
    total_debit: float
    total_credit: float
    is_balanced: bool
    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    document: DocumentRead
    pipeline_status: str
    detected_type: str
    explanation: list[str]
    extracted_fields: dict
    created_invoice: InvoiceRead | None = None
    proposed_journal_entry: JournalEntryRead | None = None


class AccountCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=12, pattern=r"^[0-9]+$")
    name: str
    group: int = Field(..., ge=1, le=9)
    category: str = Field(..., examples=["asset", "liability", "equity", "expense", "income"])
    normal_balance: str = Field(..., examples=["debit", "credit"])
    financial_statement: str = Field(..., examples=["balance_sheet", "profit_and_loss"])
    vat_behavior: str = "none"
    reconcilable: bool = False
    is_active: bool = True


class AccountRead(AccountCreate):
    id: str
    company_id: str
    model_config = {"from_attributes": True}


class AccountSeedResult(BaseModel):
    company_id: str
    created_accounts: int
