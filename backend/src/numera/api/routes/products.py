import re
import unicodedata
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from numera.api.dependencies import get_current_user, require_company_roles
from numera.api.schemas.products import (
    PriceObservationCreate,
    PriceObservationRead,
    ProductCreate,
    ProductRead,
    ProductUpdate,
    SupplierOfferRead,
    SupplierPriceComparisonRead,
    ProductPriceAnalysisRead,
    PriceAlertRead,
    SupplierProductCreate,
    SupplierProductRead,
    SupplierProductUpdate,
)
from numera.infrastructure.database.session import get_db
from numera.infrastructure.persistence.models import (
    CompanyMembershipORM,
    ProductORM,
    ProductPriceHistoryORM,
    SupplierORM,
    SupplierProductORM,
    UserORM,
)

router = APIRouter()

WRITE_ROLES = ("owner", "admin", "accountant", "manager")
READ_ROLES = WRITE_ROLES + ("employee", "readonly")


def normalize_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    return re.sub(r"\s+", " ", value)


def _active_company(user: UserORM) -> str:
    if not user.company_id:
        raise HTTPException(status_code=409, detail="No active company selected")
    return user.company_id


def _product_or_404(db: Session, company_id: str, product_id: str) -> ProductORM:
    product = db.get(ProductORM, product_id)
    if product is None or product.company_id != company_id:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def _supplier_or_404(db: Session, company_id: str, supplier_id: str) -> SupplierORM:
    supplier = db.get(SupplierORM, supplier_id)
    if supplier is None or supplier.company_id != company_id:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


def _supplier_product_or_404(
    db: Session, company_id: str, supplier_product_id: str
) -> SupplierProductORM:
    row = db.get(SupplierProductORM, supplier_product_id)
    if row is None or row.company_id != company_id:
        raise HTTPException(status_code=404, detail="Supplier product not found")
    return row


def _supplier_product_read(db: Session, row: SupplierProductORM) -> SupplierProductRead:
    supplier = db.get(SupplierORM, row.supplier_id)
    product = db.get(ProductORM, row.product_id)
    latest = (
        db.query(ProductPriceHistoryORM)
        .filter(ProductPriceHistoryORM.supplier_product_id == row.id)
        .order_by(ProductPriceHistoryORM.observed_at.desc(), ProductPriceHistoryORM.created_at.desc())
        .first()
    )
    return SupplierProductRead(
        **{column.name: getattr(row, column.name) for column in row.__table__.columns},
        supplier_name=supplier.name if supplier else None,
        product_name=product.name if product else None,
        latest_price=latest.unit_price if latest else None,
        latest_price_date=latest.observed_at if latest else None,
    )


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    _: CompanyMembershipORM = Depends(require_company_roles(*WRITE_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _active_company(user)
    product = ProductORM(
        company_id=company_id,
        normalized_name=normalize_name(payload.name),
        **payload.model_dump(),
    )
    db.add(product)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="A product with this name or internal SKU already exists"
        ) from exc
    db.refresh(product)
    return product


@router.get("/", response_model=list[ProductRead])
def list_products(
    search: str | None = Query(default=None),
    category: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    _: CompanyMembershipORM = Depends(require_company_roles(*READ_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ProductORM).filter(ProductORM.company_id == _active_company(user))
    if active_only:
        query = query.filter(ProductORM.is_active.is_(True))
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            (ProductORM.name.ilike(term)) | (ProductORM.internal_sku.ilike(term))
        )
    if category:
        query = query.filter(ProductORM.category == category)
    return query.order_by(ProductORM.name.asc()).all()




def _money(value) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _percent_change(current: Decimal, previous: Decimal) -> Decimal | None:
    if previous == 0:
        return None
    return ((current - previous) / previous * Decimal("100")).quantize(Decimal("0.01"))


@router.get("/price-alerts", response_model=list[PriceAlertRead])
def price_alerts(
    threshold_percent: Decimal = Query(default=Decimal("5"), ge=0),
    direction: str = Query(default="both", pattern="^(both|increase|decrease)$"),
    limit: int = Query(default=100, ge=1, le=500),
    _: CompanyMembershipORM = Depends(require_company_roles(*READ_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _active_company(user)
    links = db.query(SupplierProductORM).filter(
        SupplierProductORM.company_id == company_id,
        SupplierProductORM.is_active.is_(True),
    ).all()
    alerts: list[PriceAlertRead] = []
    for link in links:
        rows = db.query(ProductPriceHistoryORM).filter(
            ProductPriceHistoryORM.company_id == company_id,
            ProductPriceHistoryORM.supplier_product_id == link.id,
        ).order_by(
            ProductPriceHistoryORM.observed_at.desc(),
            ProductPriceHistoryORM.created_at.desc(),
        ).limit(2).all()
        if len(rows) < 2:
            continue
        latest, previous = rows[0], rows[1]
        latest_price = _money(latest.unit_price)
        previous_price = _money(previous.unit_price)
        change_pct = _percent_change(latest_price, previous_price)
        if change_pct is None or abs(change_pct) < threshold_percent:
            continue
        alert_direction = "increase" if change_pct > 0 else "decrease"
        if direction != "both" and direction != alert_direction:
            continue
        product = db.get(ProductORM, link.product_id)
        supplier = db.get(SupplierORM, link.supplier_id)
        if not product or not supplier:
            continue
        alerts.append(PriceAlertRead(
            product_id=product.id, product_name=product.name,
            supplier_id=supplier.id, supplier_name=supplier.name,
            supplier_reference=link.supplier_reference,
            previous_price=previous_price, previous_date=previous.observed_at,
            latest_price=latest_price, latest_date=latest.observed_at,
            change_amount=(latest_price-previous_price).quantize(Decimal("0.000001")),
            change_percent=change_pct, direction=alert_direction,
            currency=latest.currency,
        ))
    alerts.sort(key=lambda x: abs(x.change_percent), reverse=True)
    return alerts[:limit]


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: str,
    _: CompanyMembershipORM = Depends(require_company_roles(*READ_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _product_or_404(db, _active_company(user), product_id)


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: str,
    payload: ProductUpdate,
    _: CompanyMembershipORM = Depends(require_company_roles(*WRITE_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = _product_or_404(db, _active_company(user), product_id)
    changes = payload.model_dump(exclude_unset=True)
    if "name" in changes:
        changes["normalized_name"] = normalize_name(changes["name"])
    for key, value in changes.items():
        setattr(product, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Product name or SKU already in use") from exc
    db.refresh(product)
    return product


@router.get("/{product_id}/supplier-offers", response_model=list[SupplierOfferRead])
def compare_supplier_offers(
    product_id: str,
    _: CompanyMembershipORM = Depends(require_company_roles(*READ_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _active_company(user)
    _product_or_404(db, company_id, product_id)
    links = (
        db.query(SupplierProductORM, SupplierORM)
        .join(SupplierORM, SupplierORM.id == SupplierProductORM.supplier_id)
        .filter(
            SupplierProductORM.company_id == company_id,
            SupplierProductORM.product_id == product_id,
            SupplierProductORM.is_active.is_(True),
        )
        .all()
    )
    result = []
    for link, supplier in links:
        prices = db.query(ProductPriceHistoryORM).filter(
            ProductPriceHistoryORM.supplier_product_id == link.id
        )
        latest = prices.order_by(
            ProductPriceHistoryORM.observed_at.desc(), ProductPriceHistoryORM.created_at.desc()
        ).first()
        result.append(SupplierOfferRead(
            supplier_id=supplier.id,
            supplier_name=supplier.name,
            supplier_product_id=link.id,
            supplier_reference=link.supplier_reference,
            supplier_description=link.supplier_description,
            unit=link.purchase_unit,
            latest_price=latest.unit_price if latest else None,
            latest_price_date=latest.observed_at if latest else None,
            currency=link.currency,
            observations=prices.count(),
        ))
    return sorted(
        result,
        key=lambda offer: (offer.latest_price is None, offer.latest_price or Decimal("0")),
    )


@router.get("/{product_id}/price-history", response_model=list[PriceObservationRead])
def product_price_history(
    product_id: str,
    supplier_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    _: CompanyMembershipORM = Depends(require_company_roles(*READ_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _active_company(user)
    _product_or_404(db, company_id, product_id)
    query = db.query(ProductPriceHistoryORM).filter(
        ProductPriceHistoryORM.company_id == company_id,
        ProductPriceHistoryORM.product_id == product_id,
    )
    if supplier_id:
        query = query.filter(ProductPriceHistoryORM.supplier_id == supplier_id)
    rows = query.order_by(
        ProductPriceHistoryORM.observed_at.desc(), ProductPriceHistoryORM.created_at.desc()
    ).limit(limit).all()
    result = []
    for row in rows:
        supplier = db.get(SupplierORM, row.supplier_id)
        link = db.get(SupplierProductORM, row.supplier_product_id)
        result.append(PriceObservationRead(
            **{column.name: getattr(row, column.name) for column in row.__table__.columns},
            supplier_name=supplier.name if supplier else None,
            supplier_reference=link.supplier_reference if link else None,
        ))
    return result


@router.post(
    "/suppliers/{supplier_id}",
    response_model=SupplierProductRead,
    status_code=status.HTTP_201_CREATED,
)
def link_supplier_product(
    supplier_id: str,
    payload: SupplierProductCreate,
    _: CompanyMembershipORM = Depends(require_company_roles(*WRITE_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _active_company(user)
    _supplier_or_404(db, company_id, supplier_id)
    _product_or_404(db, company_id, payload.product_id)
    link = SupplierProductORM(company_id=company_id, supplier_id=supplier_id, **payload.model_dump())
    db.add(link)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This supplier reference already exists or the product is already linked",
        ) from exc
    db.refresh(link)
    return _supplier_product_read(db, link)


@router.get("/suppliers/{supplier_id}/catalog", response_model=list[SupplierProductRead])
def supplier_catalog(
    supplier_id: str,
    active_only: bool = Query(default=True),
    _: CompanyMembershipORM = Depends(require_company_roles(*READ_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _active_company(user)
    _supplier_or_404(db, company_id, supplier_id)
    query = db.query(SupplierProductORM).filter(
        SupplierProductORM.company_id == company_id,
        SupplierProductORM.supplier_id == supplier_id,
    )
    if active_only:
        query = query.filter(SupplierProductORM.is_active.is_(True))
    return [_supplier_product_read(db, row) for row in query.order_by(
        SupplierProductORM.supplier_description.asc()
    ).all()]


@router.patch("/supplier-products/{supplier_product_id}", response_model=SupplierProductRead)
def update_supplier_product(
    supplier_product_id: str,
    payload: SupplierProductUpdate,
    _: CompanyMembershipORM = Depends(require_company_roles(*WRITE_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = _supplier_product_or_404(db, _active_company(user), supplier_product_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value.upper() if key == "currency" and value else value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Supplier reference already in use") from exc
    db.refresh(row)
    return _supplier_product_read(db, row)


@router.post(
    "/supplier-products/{supplier_product_id}/prices",
    response_model=PriceObservationRead,
    status_code=status.HTTP_201_CREATED,
)
def register_price_observation(
    supplier_product_id: str,
    payload: PriceObservationCreate,
    _: CompanyMembershipORM = Depends(require_company_roles(*WRITE_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _active_company(user)
    link = _supplier_product_or_404(db, company_id, supplier_product_id)
    observation = ProductPriceHistoryORM(
        company_id=company_id,
        supplier_product_id=link.id,
        product_id=link.product_id,
        supplier_id=link.supplier_id,
        **payload.model_dump(),
    )
    db.add(observation)
    db.commit()
    db.refresh(observation)
    supplier = db.get(SupplierORM, link.supplier_id)
    return PriceObservationRead(
        **{column.name: getattr(observation, column.name) for column in observation.__table__.columns},
        supplier_name=supplier.name if supplier else None,
        supplier_reference=link.supplier_reference,
    )


@router.get("/{product_id}/price-analysis", response_model=ProductPriceAnalysisRead)
def product_price_analysis(
    product_id: str,
    supplier_id: str | None = Query(default=None),
    date_from: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    date_to: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    _: CompanyMembershipORM = Depends(require_company_roles(*READ_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id = _active_company(user)
    product = _product_or_404(db, company_id, product_id)
    query = db.query(ProductPriceHistoryORM).filter(
        ProductPriceHistoryORM.company_id == company_id,
        ProductPriceHistoryORM.product_id == product_id,
    )
    if supplier_id:
        query = query.filter(ProductPriceHistoryORM.supplier_id == supplier_id)
    if date_from:
        query = query.filter(ProductPriceHistoryORM.observed_at >= date_from)
    if date_to:
        query = query.filter(ProductPriceHistoryORM.observed_at <= date_to)
    rows = query.order_by(ProductPriceHistoryORM.observed_at.asc(), ProductPriceHistoryORM.created_at.asc()).all()
    if not rows:
        return ProductPriceAnalysisRead(
            product_id=product.id, product_name=product.name, currency=None, observations=0, suppliers=0,
            first_price=None, first_price_date=None, previous_price=None, previous_price_date=None,
            latest_price=None, latest_price_date=None, minimum_price=None, maximum_price=None,
            average_price=None, weighted_average_price=None, change_amount=None, change_percent=None,
            trend="insufficient_data",
        )
    prices=[_money(r.unit_price) for r in rows]
    latest=rows[-1]; first=rows[0]; previous=rows[-2] if len(rows)>1 else None
    avg=(sum(prices, Decimal("0"))/Decimal(len(prices))).quantize(Decimal("0.000001"))
    weighted_rows=[r for r in rows if r.quantity is not None and _money(r.quantity)>0]
    weighted=None
    if weighted_rows:
        total_qty=sum((_money(r.quantity) for r in weighted_rows), Decimal("0"))
        weighted=(sum((_money(r.unit_price)*_money(r.quantity) for r in weighted_rows), Decimal("0"))/total_qty).quantize(Decimal("0.000001"))
    latest_price=_money(latest.unit_price)
    previous_price=_money(previous.unit_price) if previous else None
    change=(latest_price-previous_price).quantize(Decimal("0.000001")) if previous_price is not None else None
    pct=_percent_change(latest_price, previous_price) if previous_price is not None else None
    trend="insufficient_data" if pct is None else ("up" if pct>0 else "down" if pct<0 else "stable")
    return ProductPriceAnalysisRead(
        product_id=product.id, product_name=product.name, currency=latest.currency,
        observations=len(rows), suppliers=len({r.supplier_id for r in rows}),
        first_price=_money(first.unit_price), first_price_date=first.observed_at,
        previous_price=previous_price, previous_price_date=previous.observed_at if previous else None,
        latest_price=latest_price, latest_price_date=latest.observed_at,
        minimum_price=min(prices), maximum_price=max(prices), average_price=avg,
        weighted_average_price=weighted, change_amount=change, change_percent=pct, trend=trend,
    )


@router.get("/{product_id}/supplier-comparison", response_model=list[SupplierPriceComparisonRead])
def supplier_price_comparison(
    product_id: str,
    date_from: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    date_to: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    _: CompanyMembershipORM = Depends(require_company_roles(*READ_ROLES)),
    user: UserORM = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    company_id=_active_company(user)
    _product_or_404(db, company_id, product_id)
    links=db.query(SupplierProductORM).filter(
        SupplierProductORM.company_id==company_id, SupplierProductORM.product_id==product_id,
        SupplierProductORM.is_active.is_(True),
    ).all()
    raw=[]
    for link in links:
        q=db.query(ProductPriceHistoryORM).filter(ProductPriceHistoryORM.supplier_product_id==link.id)
        if date_from: q=q.filter(ProductPriceHistoryORM.observed_at>=date_from)
        if date_to: q=q.filter(ProductPriceHistoryORM.observed_at<=date_to)
        rows=q.order_by(ProductPriceHistoryORM.observed_at.asc(), ProductPriceHistoryORM.created_at.asc()).all()
        if not rows: continue
        supplier=db.get(SupplierORM, link.supplier_id)
        prices=[_money(r.unit_price) for r in rows]
        raw.append((link,supplier,rows,prices))
    if not raw: return []
    best=min(_money(rows[-1].unit_price) for _,_,rows,_ in raw)
    result=[]
    for link,supplier,rows,prices in raw:
        latest=_money(rows[-1].unit_price)
        diff=(latest-best).quantize(Decimal("0.000001"))
        diff_pct=_percent_change(latest,best) if best else None
        result.append(SupplierPriceComparisonRead(
            supplier_id=supplier.id, supplier_name=supplier.name, supplier_product_id=link.id,
            supplier_reference=link.supplier_reference, supplier_description=link.supplier_description,
            unit=link.purchase_unit, currency=rows[-1].currency, observations=len(rows),
            latest_price=latest, latest_price_date=rows[-1].observed_at,
            minimum_price=min(prices), maximum_price=max(prices),
            average_price=(sum(prices,Decimal("0"))/Decimal(len(prices))).quantize(Decimal("0.000001")),
            difference_from_best=diff, difference_from_best_percent=diff_pct, is_best_price=(latest==best),
        ))
    return sorted(result,key=lambda x:x.latest_price)
