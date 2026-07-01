from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CompanyCreate(BaseModel):
    name: str
    country: str = "ES"
    currency: str = "EUR"


class CompanyResponse(BaseModel):
    id: str
    name: str
    country: str
    currency: str


@router.post("/", response_model=CompanyResponse)
def create_company(payload: CompanyCreate):
    # Temporary in-memory response for v0.1.
    # Persistence will be added in the database layer.
    return CompanyResponse(
        id="company_demo_001",
        name=payload.name,
        country=payload.country,
        currency=payload.currency,
    )
