from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from numera.domain.accounting.models import ChartAccount
from numera.domain.schemas import AccountCreate, AccountRead, AccountSeedResult
from numera.engines.chart_of_accounts.engine import ChartOfAccountsEngine
from numera.infrastructure.database.session import get_db
from numera.infrastructure.repositories import AccountRepository

router = APIRouter()


def _engine(db: Session) -> ChartOfAccountsEngine:
    return ChartOfAccountsEngine(AccountRepository(db))


@router.get("/", response_model=list[AccountRead])
def list_accounts(
    company_id: str = Query(..., description="Company whose chart of accounts will be queried"),
    category: str | None = Query(default=None),
    active_only: bool = Query(default=True),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return _engine(db).list(company_id, category=category, active_only=active_only, search=search)


@router.get("/{code}", response_model=AccountRead)
def get_account(code: str, company_id: str = Query(...), db: Session = Depends(get_db)):
    account = _engine(db).get(company_id, code)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post("/", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate, company_id: str = Query(...), db: Session = Depends(get_db)):
    try:
        return _engine(db).create(company_id, ChartAccount(**payload.model_dump()))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/seed", response_model=AccountSeedResult)
def seed_accounts(company_id: str = Query(...), db: Session = Depends(get_db)):
    created = _engine(db).seed_defaults(company_id)
    return AccountSeedResult(company_id=company_id, created_accounts=created)
