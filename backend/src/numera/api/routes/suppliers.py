from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from numera.domain.schemas import SupplierCreate, SupplierRead, SupplierResolveRequest
from numera.engines.master_data.engine import MasterDataEngine
from numera.infrastructure.database.session import get_db
from numera.infrastructure.repositories import SupplierRepository

router = APIRouter()


@router.post("/", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)):
    return SupplierRepository(db).create(payload)


@router.post("/resolve", response_model=SupplierRead)
def resolve_supplier(payload: SupplierResolveRequest, db: Session = Depends(get_db)):
    supplier = MasterDataEngine(SupplierRepository(db)).resolve_supplier(
        payload.company_id,
        payload.name,
    )
    if supplier is None:
        raise HTTPException(status_code=422, detail="A supplier name is required")
    return supplier


@router.get("/", response_model=list[SupplierRead])
def list_suppliers(
    company_id: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    suppliers = SupplierRepository(db).list()
    if company_id:
        suppliers = [supplier for supplier in suppliers if supplier.company_id == company_id]
    if search:
        value = search.casefold()
        suppliers = [supplier for supplier in suppliers if value in supplier.name.casefold()]
    return suppliers
