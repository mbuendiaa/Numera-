from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator

Money = Decimal


class TaxRateCreate(BaseModel):
    code: str = Field(min_length=2, max_length=30, pattern=r"^[A-Z0-9_-]+$")
    name: str = Field(min_length=2, max_length=120)
    rate: Decimal = Field(ge=0, le=100)
    surcharge_rate: Decimal = Field(default=0, ge=0, le=20)
    scope: Literal["domestic", "intra_eu", "export", "import"] = "domestic"
    kind: Literal["vat", "withholding", "other"] = "vat"
    deductible_percent: Decimal = Field(default=100, ge=0, le=100)
    is_exempt: bool = False
    reverse_charge: bool = False
    is_active: bool = True


class TaxRateUpdate(BaseModel):
    name: str | None = None
    rate: Decimal | None = Field(default=None, ge=0, le=100)
    surcharge_rate: Decimal | None = Field(default=None, ge=0, le=20)
    deductible_percent: Decimal | None = Field(default=None, ge=0, le=100)
    is_exempt: bool | None = None
    reverse_charge: bool | None = None
    is_active: bool | None = None


class TaxRateRead(TaxRateCreate):
    id: str
    company_id: str
    model_config = {"from_attributes": True}


class TaxLineCreate(BaseModel):
    description: str = Field(min_length=1)
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    discount_percent: Decimal = Field(default=0, ge=0, le=100)
    tax_rate_id: str
    account_code: str | None = None


class TaxLineRead(TaxLineCreate):
    id: str
    position: int
    base_amount: Decimal
    tax_amount: Decimal
    surcharge_amount: Decimal
    total_amount: Decimal
    model_config = {"from_attributes": True}


class TaxDocumentCreate(BaseModel):
    document_type: Literal["sale_invoice", "purchase_invoice", "sale_credit_note", "purchase_credit_note"]
    number: str = Field(min_length=1, max_length=80)
    counterparty_name: str = Field(min_length=1, max_length=180)
    counterparty_tax_id: str | None = None
    issue_date: str
    due_date: str | None = None
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    source_document_id: str | None = None
    lines: list[TaxLineCreate] = Field(min_length=1)

    @field_validator("currency")
    @classmethod
    def upper_currency(cls, value: str) -> str:
        return value.upper()


class TaxDocumentRead(BaseModel):
    id: str
    company_id: str
    document_type: str
    number: str
    counterparty_name: str
    counterparty_tax_id: str | None
    issue_date: str
    due_date: str | None
    currency: str
    status: str
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    surcharge_total: Decimal
    total: Decimal
    source_document_id: str | None
    lines: list[TaxLineRead]


class VatBreakdown(BaseModel):
    rate: Decimal
    base: Decimal
    vat: Decimal
    surcharge: Decimal


class VatSummary(BaseModel):
    period_start: str
    period_end: str
    output_base: Decimal
    output_vat: Decimal
    input_base: Decimal
    input_vat: Decimal
    deductible_input_vat: Decimal
    vat_due: Decimal
    sales_by_rate: list[VatBreakdown]
    purchases_by_rate: list[VatBreakdown]


class VATSettlementCreate(BaseModel):
    period_start: str
    period_end: str


class VATSettlementRead(BaseModel):
    id: str
    company_id: str
    period_start: str
    period_end: str
    output_base: Decimal
    output_vat: Decimal
    input_base: Decimal
    input_vat: Decimal
    deductible_input_vat: Decimal
    vat_due: Decimal
    status: str
    model_config = {"from_attributes": True}
