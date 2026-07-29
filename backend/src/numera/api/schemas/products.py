from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator


UnitCode = Literal["kg", "g", "unit", "box", "litre", "pack", "other"]


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=240)
    category: str | None = Field(default=None, max_length=120)
    base_unit: UnitCode = "unit"
    default_vat_rate: Decimal | None = Field(default=None, ge=0, le=100)
    internal_sku: str | None = Field(default=None, max_length=80)
    notes: str | None = None

    @field_validator("name", "category", "internal_sku", mode="before")
    @classmethod
    def strip_text(cls, value):
        return value.strip() if isinstance(value, str) else value


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=240)
    category: str | None = Field(default=None, max_length=120)
    base_unit: UnitCode | None = None
    default_vat_rate: Decimal | None = Field(default=None, ge=0, le=100)
    internal_sku: str | None = Field(default=None, max_length=80)
    notes: str | None = None
    is_active: bool | None = None


class ProductRead(BaseModel):
    id: str
    company_id: str
    name: str
    normalized_name: str
    category: str | None
    base_unit: str
    default_vat_rate: Decimal | None
    internal_sku: str | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SupplierProductCreate(BaseModel):
    product_id: str
    supplier_reference: str = Field(min_length=1, max_length=100)
    supplier_description: str = Field(min_length=2, max_length=300)
    purchase_unit: UnitCode = "unit"
    package_unit: UnitCode | None = None
    units_per_package: Decimal | None = Field(default=None, gt=0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    default_vat_rate: Decimal | None = Field(default=None, ge=0, le=100)
    notes: str | None = None

    @field_validator("supplier_reference", "supplier_description", mode="before")
    @classmethod
    def strip_required(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, value: str) -> str:
        return value.upper()


class SupplierProductUpdate(BaseModel):
    supplier_reference: str | None = Field(default=None, min_length=1, max_length=100)
    supplier_description: str | None = Field(default=None, min_length=2, max_length=300)
    purchase_unit: UnitCode | None = None
    package_unit: UnitCode | None = None
    units_per_package: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    default_vat_rate: Decimal | None = Field(default=None, ge=0, le=100)
    notes: str | None = None
    is_active: bool | None = None


class SupplierProductRead(BaseModel):
    id: str
    company_id: str
    supplier_id: str
    product_id: str
    supplier_reference: str
    supplier_description: str
    purchase_unit: str
    package_unit: str | None
    units_per_package: Decimal | None
    currency: str
    default_vat_rate: Decimal | None
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    supplier_name: str | None = None
    product_name: str | None = None
    latest_price: Decimal | None = None
    latest_price_date: str | None = None

    model_config = {"from_attributes": True}


class PriceObservationCreate(BaseModel):
    unit_price: Decimal = Field(gt=0)
    observed_at: str = Field(description="Invoice or price date in YYYY-MM-DD format")
    quantity: Decimal | None = Field(default=None, gt=0)
    package_quantity: Decimal | None = Field(default=None, gt=0)
    net_amount: Decimal | None = Field(default=None, ge=0)
    vat_rate: Decimal | None = Field(default=None, ge=0, le=100)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    invoice_id: str | None = None
    invoice_number: str | None = Field(default=None, max_length=100)
    source_document_id: str | None = None
    lot_number: str | None = Field(default=None, max_length=100)
    delivery_note_number: str | None = Field(default=None, max_length=100)

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, value: str) -> str:
        return value.upper()


class PriceObservationRead(BaseModel):
    id: str
    company_id: str
    supplier_product_id: str
    product_id: str
    supplier_id: str
    unit_price: Decimal
    observed_at: str
    quantity: Decimal | None
    package_quantity: Decimal | None
    net_amount: Decimal | None
    vat_rate: Decimal | None
    currency: str
    invoice_id: str | None
    invoice_number: str | None
    source_document_id: str | None
    lot_number: str | None
    delivery_note_number: str | None
    created_at: datetime
    supplier_name: str | None = None
    supplier_reference: str | None = None

    model_config = {"from_attributes": True}


class SupplierOfferRead(BaseModel):
    supplier_id: str
    supplier_name: str
    supplier_product_id: str
    supplier_reference: str
    supplier_description: str
    unit: str
    latest_price: Decimal | None
    latest_price_date: str | None
    currency: str
    observations: int
