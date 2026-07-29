import re
import unicodedata
from decimal import Decimal

from sqlalchemy.orm import Session

from numera.infrastructure.persistence.models import (
    ProductORM,
    ProductPriceHistoryORM,
    SupplierORM,
    SupplierProductORM,
)


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    return re.sub(r"\s+", " ", value)


class InvoiceCatalogService:
    """Creates/reuses product master data from extracted invoice lines."""

    def __init__(self, db: Session):
        self.db = db

    def process(self, *, company_id: str, supplier: SupplierORM | None, invoice, document_id: str, fields: dict):
        if supplier is None:
            return []
        lines = self._value(fields, "line_items") or []
        vat_rate = self._value(fields, "vat_rate")
        invoice_date = self._value(fields, "invoice_date") or "unknown"
        created = []
        for line in lines:
            ref = str(line.get("supplier_reference") or "").strip()
            description = str(line.get("description") or "").strip()
            if not ref or not description:
                continue
            link = (
                self.db.query(SupplierProductORM)
                .filter(
                    SupplierProductORM.company_id == company_id,
                    SupplierProductORM.supplier_id == supplier.id,
                    SupplierProductORM.supplier_reference == ref,
                )
                .first()
            )
            if link is None:
                normalized = normalize_name(description)
                product = (
                    self.db.query(ProductORM)
                    .filter(ProductORM.company_id == company_id, ProductORM.normalized_name == normalized)
                    .first()
                )
                if product is None:
                    product = ProductORM(
                        company_id=company_id,
                        name=description.title(),
                        normalized_name=normalized,
                        category="Unclassified",
                        base_unit=line.get("purchase_unit") or "unit",
                        default_vat_rate=vat_rate,
                        internal_sku=None,
                        notes="Created automatically from invoice extraction",
                    )
                    self.db.add(product)
                    self.db.flush()
                link = SupplierProductORM(
                    company_id=company_id,
                    supplier_id=supplier.id,
                    product_id=product.id,
                    supplier_reference=ref,
                    supplier_description=description,
                    purchase_unit=line.get("purchase_unit") or "unit",
                    package_unit=line.get("package_unit"),
                    currency=self._value(fields, "currency") or "EUR",
                    default_vat_rate=vat_rate,
                    notes="Created automatically from invoice extraction",
                )
                self.db.add(link)
                self.db.flush()
            duplicate = (
                self.db.query(ProductPriceHistoryORM)
                .filter(
                    ProductPriceHistoryORM.source_document_id == document_id,
                    ProductPriceHistoryORM.supplier_product_id == link.id,
                )
                .first()
            )
            if duplicate is None and line.get("unit_price") is not None:
                observation = ProductPriceHistoryORM(
                    company_id=company_id,
                    supplier_product_id=link.id,
                    product_id=link.product_id,
                    supplier_id=supplier.id,
                    unit_price=Decimal(str(line["unit_price"])),
                    observed_at=self._iso_date(invoice_date),
                    quantity=line.get("quantity"),
                    package_quantity=line.get("package_quantity"),
                    net_amount=line.get("net_amount"),
                    vat_rate=vat_rate,
                    currency=self._value(fields, "currency") or "EUR",
                    invoice_id=invoice.id if invoice else None,
                    invoice_number=invoice.invoice_number if invoice else self._value(fields, "invoice_number"),
                    source_document_id=document_id,
                    lot_number=line.get("lot_number"),
                    delivery_note_number=line.get("delivery_note_number"),
                )
                self.db.add(observation)
            created.append({"supplier_product_id": link.id, "product_id": link.product_id, "reference": ref})
        self.db.commit()
        return created

    @staticmethod
    def _value(fields: dict, name: str):
        field = fields.get(name)
        return field.get("value") if field else None

    @staticmethod
    def _iso_date(value: str) -> str:
        match = re.match(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", str(value))
        if not match:
            return str(value)[:10]
        day, month, year = match.groups()
        if len(year) == 2:
            year = "20" + year
        return f"{year}-{int(month):02d}-{int(day):02d}"
