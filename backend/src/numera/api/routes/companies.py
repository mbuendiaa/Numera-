from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from numera.domain.schemas import CompanyCreate, CompanyRead
from numera.infrastructure.database.session import get_db
from numera.infrastructure.repositories import CompanyRepository

router = APIRouter()


@router.post("/", response_model=CompanyRead)
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    return CompanyRepository(db).create(payload)


@router.get("/", response_model=list[CompanyRead])
def list_companies(db: Session = Depends(get_db)):
    return CompanyRepository(db).list()
