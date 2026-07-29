from collections import defaultdict
from datetime import date
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from numera.api.dependencies import get_active_membership
from numera.api.schemas.intelligence import (
    ClassificationRead, DashboardRead, ProductAnalyticsRead, ReviewCenterRead,
    ReviewItemRead, SupplierAnalyticsRead,
)
from numera.infrastructure.database.session import get_db
from numera.infrastructure.persistence.models import (
    DocumentORM, InvoiceORM, JournalEntryORM, ProductORM, ProductPriceHistoryORM,
    SupplierORM, SupplierProductORM,
)
from numera.services.accounting_intelligence import classify_purchase

router = APIRouter()


def _company(membership) -> str:
    return membership.company_id


@router.get("/classify/invoice/{invoice_id}", response_model=ClassificationRead)
def classify_invoice(invoice_id: str, membership=Depends(get_active_membership), db: Session = Depends(get_db)):
    company_id = _company(membership)
    invoice = db.query(InvoiceORM).filter(InvoiceORM.id == invoice_id, InvoiceORM.company_id == company_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    supplier = db.get(SupplierORM, invoice.supplier_id) if invoice.supplier_id else None
    result = classify_purchase(
        supplier_name=supplier.name if supplier else None,
        description=f"{supplier.name if supplier else ''} {invoice.invoice_number}",
        supplier_default_account=supplier.default_account if supplier else None,
    )
    return ClassificationRead(**result.__dict__)


@router.get("/review", response_model=ReviewCenterRead)
def review_center(
    confidence_threshold: float = Query(default=0.75, ge=0, le=1),
    membership=Depends(get_active_membership),
    db: Session = Depends(get_db),
):
    company_id = _company(membership)
    items: list[ReviewItemRead] = []

    documents = db.query(DocumentORM).filter(DocumentORM.company_id == company_id).all()
    ocr_errors = 0
    for doc in documents:
        try:
            fields = json.loads(doc.extracted_fields_json or "{}")
        except json.JSONDecodeError:
            fields = {}
        preview = (doc.extracted_text_preview or "").strip()
        if doc.status in {"error", "failed"} or (doc.document_type == "invoice" and not preview and not fields):
            ocr_errors += 1
            items.append(ReviewItemRead(id=doc.id, item_type="document", reason="OCR extraction incomplete", status=doc.status, created_at=doc.created_at.isoformat(), reference=doc.filename))

    low_confidence = 0
    invoices = db.query(InvoiceORM).filter(InvoiceORM.company_id == company_id).all()
    suppliers = {s.id: s for s in db.query(SupplierORM).filter(SupplierORM.company_id == company_id).all()}
    seen = defaultdict(list)
    for inv in invoices:
        supplier = suppliers.get(inv.supplier_id)
        result = classify_purchase(supplier_name=supplier.name if supplier else None, description=inv.invoice_number, supplier_default_account=supplier.default_account if supplier else None)
        if result.confidence < confidence_threshold:
            low_confidence += 1
            items.append(ReviewItemRead(id=inv.id, item_type="invoice", reason=f"Low accounting confidence: {result.reason}", confidence=result.confidence, status=inv.status, created_at=inv.created_at.isoformat(), reference=inv.invoice_number))
        seen[(inv.supplier_id, inv.invoice_number.strip().upper())].append(inv)

    duplicate_candidates = 0
    for group in seen.values():
        if len(group) > 1:
            duplicate_candidates += len(group)
            for inv in group:
                items.append(ReviewItemRead(id=inv.id, item_type="invoice", reason="Possible duplicate invoice", status=inv.status, created_at=inv.created_at.isoformat(), reference=inv.invoice_number))

    accounting_errors = 0
    entries = db.query(JournalEntryORM).filter(JournalEntryORM.company_id == company_id).all()
    for entry in entries:
        if abs(float(entry.total_debit) - float(entry.total_credit)) > 0.02:
            accounting_errors += 1
            items.append(ReviewItemRead(id=entry.id, item_type="journal", reason="Journal entry is not balanced", status=entry.status, reference=entry.description))

    items.sort(key=lambda x: x.created_at or "", reverse=True)
    return ReviewCenterRead(company_id=company_id, total_pending=len(items), low_confidence=low_confidence, ocr_errors=ocr_errors, accounting_errors=accounting_errors, duplicate_candidates=duplicate_candidates, items=items)


@router.get("/dashboard", response_model=DashboardRead)
def dashboard(membership=Depends(get_active_membership), db: Session = Depends(get_db)):
    company_id = _company(membership)
    current_month = date.today().isoformat()[:7]
    documents = db.query(DocumentORM).filter(DocumentORM.company_id == company_id).order_by(DocumentORM.created_at.desc()).all()
    invoices = db.query(InvoiceORM).filter(InvoiceORM.company_id == company_id).all()
    entries = db.query(JournalEntryORM).filter(JournalEntryORM.company_id == company_id).all()
    month_invoices = [i for i in invoices if (i.issue_date or "").startswith(current_month)]
    review = review_center(0.75, membership, db)
    latest = [{"id": d.id, "filename": d.filename, "status": d.status, "document_type": d.document_type, "created_at": d.created_at.isoformat()} for d in documents[:10]]
    return DashboardRead(
        company_id=company_id,
        documents_processed=len(documents),
        pending_review=review.total_pending,
        proposed_entries=sum(e.status == "proposed" for e in entries),
        approved_entries=sum(e.status == "approved" for e in entries),
        posted_entries=sum(e.status == "posted" for e in entries),
        purchase_volume_month=round(sum(float(i.total_amount) for i in month_invoices), 2),
        vat_supported_month=round(sum(float(i.tax_amount) for i in month_invoices), 2),
        suppliers=db.query(SupplierORM).filter(SupplierORM.company_id == company_id).count(),
        products=db.query(ProductORM).filter(ProductORM.company_id == company_id).count(),
        price_alerts=0,
        latest_documents=latest,
    )


@router.get("/suppliers/{supplier_id}/analytics", response_model=SupplierAnalyticsRead)
def supplier_analytics(supplier_id: str, membership=Depends(get_active_membership), db: Session = Depends(get_db)):
    company_id = _company(membership)
    supplier = db.query(SupplierORM).filter(SupplierORM.id == supplier_id, SupplierORM.company_id == company_id).first()
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    invoices = db.query(InvoiceORM).filter(InvoiceORM.company_id == company_id, InvoiceORM.supplier_id == supplier_id).all()
    prices = db.query(ProductPriceHistoryORM).filter(ProductPriceHistoryORM.company_id == company_id, ProductPriceHistoryORM.supplier_id == supplier_id).all()
    total = round(sum(float(i.total_amount) for i in invoices), 2)
    latest_invoice = max((i.issue_date for i in invoices), default=None)
    latest_price = max(prices, key=lambda p: p.observed_at).unit_price if prices else None
    products = {p.product_id for p in prices}
    return SupplierAnalyticsRead(supplier_id=supplier.id, supplier_name=supplier.name, invoice_count=len(invoices), total_purchased=total, average_invoice=round(total / len(invoices), 2) if invoices else 0, products_supplied=len(products), latest_invoice_date=latest_invoice, latest_purchase_price=float(latest_price) if latest_price is not None else None)


@router.get("/products/{product_id}/analytics", response_model=ProductAnalyticsRead)
def product_analytics(product_id: str, membership=Depends(get_active_membership), db: Session = Depends(get_db)):
    company_id = _company(membership)
    product = db.query(ProductORM).filter(ProductORM.id == product_id, ProductORM.company_id == company_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    prices = db.query(ProductPriceHistoryORM).filter(ProductPriceHistoryORM.company_id == company_id, ProductPriceHistoryORM.product_id == product_id).all()
    if not prices:
        return ProductAnalyticsRead(product_id=product.id, product_name=product.name, observations=0, average_price=None, latest_price=None, latest_purchase_date=None, best_supplier=None, worst_supplier=None, purchase_frequency_days=None)
    supplier_names = {s.id: s.name for s in db.query(SupplierORM).filter(SupplierORM.company_id == company_id).all()}
    averages = defaultdict(list)
    for p in prices:
        averages[p.supplier_id].append(float(p.unit_price))
    ranked = sorted(((sum(v)/len(v), sid) for sid, v in averages.items()))
    latest = max(prices, key=lambda p: p.observed_at)
    dates = sorted({p.observed_at for p in prices})
    frequency = None
    if len(dates) > 1:
        parsed = [date.fromisoformat(d) for d in dates]
        frequency = round(sum((b-a).days for a,b in zip(parsed, parsed[1:]))/(len(parsed)-1), 2)
    best_avg, best_id = ranked[0]
    worst_avg, worst_id = ranked[-1]
    return ProductAnalyticsRead(
        product_id=product.id, product_name=product.name, observations=len(prices),
        average_price=round(sum(float(p.unit_price) for p in prices)/len(prices), 6),
        latest_price=float(latest.unit_price), latest_purchase_date=latest.observed_at,
        best_supplier={"supplier_id": best_id, "supplier_name": supplier_names.get(best_id, best_id), "average_price": round(best_avg, 6)},
        worst_supplier={"supplier_id": worst_id, "supplier_name": supplier_names.get(worst_id, worst_id), "average_price": round(worst_avg, 6)},
        purchase_frequency_days=frequency,
    )
