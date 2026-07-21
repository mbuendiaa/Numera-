from enum import StrEnum
from pydantic import BaseModel, Field, model_validator


class AccountingEventType(StrEnum):
    PURCHASE_INVOICE = "purchase_invoice"
    SALES_INVOICE = "sales_invoice"
    BANK_TRANSACTION = "bank_transaction"
    PAYROLL = "payroll"
    MANUAL_ADJUSTMENT = "manual_adjustment"


class AccountingEventSource(StrEnum):
    DOCUMENT_ENGINE = "document_engine"
    EMAIL_ENGINE = "email_engine"
    BANK_ENGINE = "bank_engine"
    API = "api"
    MANUAL = "manual"


class JournalEntryStatus(StrEnum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    APPROVED = "approved"
    POSTED = "posted"
    REJECTED = "rejected"


class AccountingEventLine(BaseModel):
    description: str
    quantity: float | None = None
    unit_price: float | None = None
    amount: float


class AccountingEventTax(BaseModel):
    tax_type: str = "VAT"
    rate: float
    base_amount: float
    tax_amount: float


class AccountingEvent(BaseModel):
    company_id: str
    event_type: AccountingEventType
    source: AccountingEventSource
    source_document_id: str | None = None
    supplier_id: str | None = None
    supplier_name: str | None = None
    customer_id: str | None = None
    customer_name: str | None = None
    event_date: str
    currency: str = "EUR"
    description: str | None = None
    lines: list[AccountingEventLine] = Field(default_factory=list)
    taxes: list[AccountingEventTax] = Field(default_factory=list)
    base_amount: float
    tax_amount: float
    total_amount: float
    metadata: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_amounts(self):
        expected_total = round(self.base_amount + self.tax_amount, 2)
        actual_total = round(self.total_amount, 2)
        if abs(expected_total - actual_total) > 0.02:
            raise ValueError(f"AccountingEvent amounts do not balance: base + tax = {expected_total}, total = {actual_total}")
        return self


class ChartAccount(BaseModel):
    code: str
    name: str
    type: str
    is_active: bool = True


class PostingRule(BaseModel):
    rule_id: str
    company_id: str
    event_type: AccountingEventType
    debit_account: str
    tax_account: str | None = None
    credit_account: str
    description: str
    priority: int = 100
    is_active: bool = True


class JournalLine(BaseModel):
    account_code: str
    account_name: str | None = None
    description: str
    debit: float = 0.0
    credit: float = 0.0

    @model_validator(mode="after")
    def validate_line(self):
        if self.debit < 0 or self.credit < 0:
            raise ValueError("Journal line amounts cannot be negative.")
        if self.debit > 0 and self.credit > 0:
            raise ValueError("Journal line cannot have both debit and credit.")
        if self.debit == 0 and self.credit == 0:
            raise ValueError("Journal line must contain either debit or credit.")
        return self


class JournalEntry(BaseModel):
    company_id: str
    event_type: AccountingEventType
    source_event_id: str | None = None
    source_document_id: str | None = None
    entry_date: str
    description: str
    status: JournalEntryStatus = JournalEntryStatus.PROPOSED
    lines: list[JournalLine]

    @property
    def total_debit(self) -> float:
        return round(sum(line.debit for line in self.lines), 2)

    @property
    def total_credit(self) -> float:
        return round(sum(line.credit for line in self.lines), 2)

    @property
    def is_balanced(self) -> bool:
        return abs(self.total_debit - self.total_credit) <= 0.02

    @model_validator(mode="after")
    def validate_entry(self):
        if len(self.lines) < 2:
            raise ValueError("Journal entry must contain at least two lines.")
        if not self.is_balanced:
            raise ValueError(f"Journal entry is not balanced: debit={self.total_debit}, credit={self.total_credit}")
        return self
