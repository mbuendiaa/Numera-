from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from numera.api.dependencies import get_current_user, require_company_roles
from numera.api.schemas.tax import (
    TaxDocumentCreate, TaxDocumentRead, TaxLineRead, TaxRateCreate, TaxRateRead,
    TaxRateUpdate, VATSettlementCreate, VATSettlementRead, VatBreakdown, VatSummary,
)
from numera.infrastructure.database.session import get_db
from numera.infrastructure.persistence.models import (
    AuditLogORM, TaxDocumentLineORM, TaxDocumentORM, TaxRateORM, UserORM, VATSettlementORM,
)

router = APIRouter()
CENT = Decimal("0.01")


def q(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def active_company(user: UserORM) -> str:
    if not user.company_id:
        raise HTTPException(status_code=409, detail="No active company selected")
    return user.company_id


def audit(db: Session, user: UserORM, action: str, entity: str, entity_id: str, details=None):
    db.add(AuditLogORM(company_id=user.company_id, user_id=user.id, action=action,
                       entity_type=entity, entity_id=entity_id,
                       details_json=json.dumps(details or {}, ensure_ascii=False)))


def serialize_document(db: Session, doc: TaxDocumentORM) -> TaxDocumentRead:
    lines = db.scalars(select(TaxDocumentLineORM).where(
        TaxDocumentLineORM.document_id == doc.id
    ).order_by(TaxDocumentLineORM.position)).all()
    return TaxDocumentRead(
        id=doc.id, company_id=doc.company_id, document_type=doc.document_type,
        number=doc.number, counterparty_name=doc.counterparty_name,
        counterparty_tax_id=doc.counterparty_tax_id, issue_date=doc.issue_date,
        due_date=doc.due_date, currency=doc.currency, status=doc.status,
        subtotal=doc.subtotal, discount_total=doc.discount_total,
        tax_total=doc.tax_total, surcharge_total=doc.surcharge_total, total=doc.total,
        source_document_id=doc.source_document_id,
        lines=[TaxLineRead.model_validate(line) for line in lines],
    )


@router.post("/rates/seed", response_model=list[TaxRateRead], status_code=201)
def seed_rates(_: object = Depends(require_company_roles("owner", "admin", "accountant")),
               user: UserORM = Depends(get_current_user), db: Session = Depends(get_db)):
    company_id = active_company(user)
    defaults = [
        ("IVA21", "IVA general 21%", 21, 0, "domestic", False, False),
        ("IVA10", "IVA reducido 10%", 10, 0, "domestic", False, False),
        ("IVA4", "IVA superreducido 4%", 4, 0, "domestic", False, False),
        ("EXENTO", "Operación exenta", 0, 0, "domestic", True, False),
        ("ISP21", "Inversión sujeto pasivo 21%", 21, 0, "domestic", False, True),
        ("INTRA21", "Intracomunitaria 21%", 21, 0, "intra_eu", False, True),
        ("EXPORT0", "Exportación 0%", 0, 0, "export", True, False),
        ("IVA21_RE52", "IVA 21% + recargo 5,2%", 21, Decimal("5.2"), "domestic", False, False),
    ]
    for code, name, rate, surcharge, scope, exempt, reverse in defaults:
        exists = db.scalar(select(TaxRateORM).where(TaxRateORM.company_id == company_id, TaxRateORM.code == code))
        if not exists:
            db.add(TaxRateORM(company_id=company_id, code=code, name=name, rate=rate,
                              surcharge_rate=surcharge, scope=scope, is_exempt=exempt,
                              reverse_charge=reverse))
    db.commit()
    return db.scalars(select(TaxRateORM).where(TaxRateORM.company_id == company_id).order_by(TaxRateORM.rate)).all()


@router.get("/rates", response_model=list[TaxRateRead])
def list_rates(include_inactive: bool = False,
               _: object = Depends(require_company_roles("owner", "admin", "accountant", "manager", "readonly")),
               user: UserORM = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(TaxRateORM).where(TaxRateORM.company_id == active_company(user))
    if not include_inactive:
        stmt = stmt.where(TaxRateORM.is_active.is_(True))
    return db.scalars(stmt.order_by(TaxRateORM.rate, TaxRateORM.code)).all()


@router.post("/rates", response_model=TaxRateRead, status_code=201)
def create_rate(payload: TaxRateCreate,
                _: object = Depends(require_company_roles("owner", "admin", "accountant")),
                user: UserORM = Depends(get_current_user), db: Session = Depends(get_db)):
    row = TaxRateORM(company_id=active_company(user), **payload.model_dump())
    db.add(row)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback(); raise HTTPException(409, "Tax code already exists") from exc
    audit(db, user, "tax_rate.created", "tax_rate", row.id)
    db.commit(); db.refresh(row); return row


@router.patch("/rates/{rate_id}", response_model=TaxRateRead)
def update_rate(rate_id: str, payload: TaxRateUpdate,
                _: object = Depends(require_company_roles("owner", "admin", "accountant")),
                user: UserORM = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.get(TaxRateORM, rate_id)
    if not row or row.company_id != active_company(user): raise HTTPException(404, "Tax rate not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(row, key, value)
    audit(db, user, "tax_rate.updated", "tax_rate", row.id)
    db.commit(); db.refresh(row); return row


@router.delete("/rates/{rate_id}", status_code=204)
def deactivate_rate(rate_id: str,
                    _: object = Depends(require_company_roles("owner", "admin")),
                    user: UserORM = Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.get(TaxRateORM, rate_id)
    if not row or row.company_id != active_company(user): raise HTTPException(404, "Tax rate not found")
    row.is_active = False; audit(db, user, "tax_rate.deactivated", "tax_rate", row.id); db.commit()


@router.post("/documents", response_model=TaxDocumentRead, status_code=201)
def create_document(payload: TaxDocumentCreate,
                    _: object = Depends(require_company_roles("owner", "admin", "accountant", "manager")),
                    user: UserORM = Depends(get_current_user), db: Session = Depends(get_db)):
    company_id = active_company(user)
    tax_ids = {line.tax_rate_id for line in payload.lines}
    rates = {r.id: r for r in db.scalars(select(TaxRateORM).where(
        TaxRateORM.company_id == company_id, TaxRateORM.id.in_(tax_ids), TaxRateORM.is_active.is_(True))).all()}
    if len(rates) != len(tax_ids): raise HTTPException(422, "One or more tax rates are invalid")
    doc = TaxDocumentORM(company_id=company_id, document_type=payload.document_type,
        number=payload.number, counterparty_name=payload.counterparty_name,
        counterparty_tax_id=payload.counterparty_tax_id, issue_date=payload.issue_date,
        due_date=payload.due_date, currency=payload.currency, source_document_id=payload.source_document_id,
        status="posted", created_by=user.id)
    db.add(doc); db.flush()
    subtotal = discount_total = tax_total = surcharge_total = Decimal("0")
    sign = Decimal("-1") if "credit_note" in payload.document_type else Decimal("1")
    for pos, line in enumerate(payload.lines, 1):
        rate = rates[line.tax_rate_id]
        gross = Decimal(line.quantity) * Decimal(line.unit_price)
        discount = gross * Decimal(line.discount_percent) / Decimal("100")
        base = q((gross - discount) * sign)
        vat = Decimal("0") if rate.is_exempt or rate.reverse_charge else q(base * Decimal(rate.rate) / Decimal("100"))
        surcharge = q(base * Decimal(rate.surcharge_rate) / Decimal("100"))
        total = q(base + vat + surcharge)
        db.add(TaxDocumentLineORM(document_id=doc.id, position=pos, description=line.description,
            quantity=line.quantity, unit_price=line.unit_price, discount_percent=line.discount_percent,
            tax_rate_id=line.tax_rate_id, account_code=line.account_code, base_amount=base,
            tax_amount=vat, surcharge_amount=surcharge, total_amount=total))
        subtotal += q(gross * sign); discount_total += q(discount * sign)
        tax_total += vat; surcharge_total += surcharge
    doc.subtotal=q(subtotal); doc.discount_total=q(discount_total); doc.tax_total=q(tax_total)
    doc.surcharge_total=q(surcharge_total); doc.total=q(subtotal-discount_total+tax_total+surcharge_total)
    try: db.flush()
    except IntegrityError as exc: db.rollback(); raise HTTPException(409, "Document number already exists") from exc
    audit(db, user, "tax_document.posted", "tax_document", doc.id, {"total": str(doc.total)})
    db.commit(); db.refresh(doc); return serialize_document(db, doc)


@router.get("/documents", response_model=list[TaxDocumentRead])
def list_documents(document_type: str | None = None, date_from: str | None = None, date_to: str | None = None,
                   _: object = Depends(require_company_roles("owner", "admin", "accountant", "manager", "readonly")),
                   user: UserORM = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(TaxDocumentORM).where(TaxDocumentORM.company_id == active_company(user))
    if document_type: stmt=stmt.where(TaxDocumentORM.document_type == document_type)
    if date_from: stmt=stmt.where(TaxDocumentORM.issue_date >= date_from)
    if date_to: stmt=stmt.where(TaxDocumentORM.issue_date <= date_to)
    docs=db.scalars(stmt.order_by(TaxDocumentORM.issue_date.desc())).all()
    return [serialize_document(db, d) for d in docs]


def summary(db: Session, company_id: str, start: str, end: str) -> VatSummary:
    docs=db.scalars(select(TaxDocumentORM).where(TaxDocumentORM.company_id==company_id,
        TaxDocumentORM.issue_date>=start, TaxDocumentORM.issue_date<=end, TaxDocumentORM.status=="posted")).all()
    output_base=output_vat=input_base=input_vat=deductible=Decimal("0")
    sales=defaultdict(lambda:[Decimal("0"),Decimal("0"),Decimal("0")])
    purchases=defaultdict(lambda:[Decimal("0"),Decimal("0"),Decimal("0")])
    for doc in docs:
        is_sale=doc.document_type.startswith("sale")
        for line in db.scalars(select(TaxDocumentLineORM).where(TaxDocumentLineORM.document_id==doc.id)).all():
            rate=db.get(TaxRateORM,line.tax_rate_id); key=Decimal(rate.rate)
            bucket=sales if is_sale else purchases; bucket[key][0]+=Decimal(line.base_amount); bucket[key][1]+=Decimal(line.tax_amount); bucket[key][2]+=Decimal(line.surcharge_amount)
            if is_sale: output_base+=Decimal(line.base_amount); output_vat+=Decimal(line.tax_amount)
            else:
                input_base+=Decimal(line.base_amount); input_vat+=Decimal(line.tax_amount)
                deductible += Decimal(line.tax_amount)*Decimal(rate.deductible_percent)/Decimal("100")
                if rate.reverse_charge:
                    reverse=q(Decimal(line.base_amount)*Decimal(rate.rate)/Decimal("100")); output_vat+=reverse; input_vat+=reverse; deductible+=reverse
    breakdown=lambda data:[VatBreakdown(rate=k,base=q(v[0]),vat=q(v[1]),surcharge=q(v[2])) for k,v in sorted(data.items())]
    return VatSummary(period_start=start,period_end=end,output_base=q(output_base),output_vat=q(output_vat),
        input_base=q(input_base),input_vat=q(input_vat),deductible_input_vat=q(deductible),
        vat_due=q(output_vat-deductible),sales_by_rate=breakdown(sales),purchases_by_rate=breakdown(purchases))


@router.get("/vat/summary", response_model=VatSummary)
def vat_summary(period_start: str=Query(...), period_end: str=Query(...),
                _: object=Depends(require_company_roles("owner","admin","accountant","readonly")),
                user: UserORM=Depends(get_current_user), db: Session=Depends(get_db)):
    return summary(db,active_company(user),period_start,period_end)


@router.post("/vat/settlements", response_model=VATSettlementRead, status_code=201)
def create_settlement(payload: VATSettlementCreate,
                      _: object=Depends(require_company_roles("owner","admin","accountant")),
                      user: UserORM=Depends(get_current_user), db: Session=Depends(get_db)):
    s=summary(db,active_company(user),payload.period_start,payload.period_end)
    row=VATSettlementORM(company_id=user.company_id,period_start=payload.period_start,period_end=payload.period_end,
        output_base=s.output_base,output_vat=s.output_vat,input_base=s.input_base,input_vat=s.input_vat,
        deductible_input_vat=s.deductible_input_vat,vat_due=s.vat_due,created_by=user.id,status="draft")
    db.add(row)
    try: db.flush()
    except IntegrityError as exc: db.rollback(); raise HTTPException(409,"Settlement already exists for this period") from exc
    audit(db,user,"vat_settlement.created","vat_settlement",row.id); db.commit(); db.refresh(row); return row


@router.get("/vat/settlements", response_model=list[VATSettlementRead])
def list_settlements(_: object=Depends(require_company_roles("owner","admin","accountant","readonly")),
                     user: UserORM=Depends(get_current_user), db: Session=Depends(get_db)):
    return db.scalars(select(VATSettlementORM).where(VATSettlementORM.company_id==active_company(user)).order_by(VATSettlementORM.period_start.desc())).all()
