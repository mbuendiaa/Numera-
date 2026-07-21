from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from numera.domain.schemas import InvoiceCreate, InvoiceRead
from numera.infrastructure.database.session import get_db
from numera.infrastructure.repositories import InvoiceRepository

router = APIRouter()


@router.post("/", response_model=InvoiceRead)
def create_invoice(payload: InvoiceCreate, db: Session = Depends(get_db)):
    return InvoiceRepository(db).create(payload)


@router.get("/", response_model=list[InvoiceRead])
def list_invoices(db: Session = Depends(get_db)):
    return InvoiceRepository(db).list()
