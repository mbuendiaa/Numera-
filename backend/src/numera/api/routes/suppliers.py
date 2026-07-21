from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from numera.domain.schemas import SupplierCreate, SupplierRead
from numera.infrastructure.database.session import get_db
from numera.infrastructure.repositories import SupplierRepository

router = APIRouter()


@router.post("/", response_model=SupplierRead)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)):
    return SupplierRepository(db).create(payload)


@router.get("/", response_model=list[SupplierRead])
def list_suppliers(db: Session = Depends(get_db)):
    return SupplierRepository(db).list()
