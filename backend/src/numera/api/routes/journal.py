from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from numera.api.serializers import journal_entry_to_read
from numera.domain.accounting.models import JournalEntryStatus
from numera.domain.schemas import JournalEntryRead
from numera.engines.ledger.engine import LedgerEngine, LedgerQuery
from numera.infrastructure.database.session import get_db
from numera.infrastructure.repositories import JournalRepository

router = APIRouter()


def _ledger(db: Session) -> LedgerEngine:
    return LedgerEngine(JournalRepository(db))


@router.get("/", response_model=list[JournalEntryRead])
def list_journal_entries(
    company_id: str | None = Query(default=None),
    entry_status: JournalEntryStatus | None = Query(default=None, alias="status"),
    date_from: str | None = Query(default=None, description="DD/MM/YYYY or YYYY-MM-DD"),
    date_to: str | None = Query(default=None, description="DD/MM/YYYY or YYYY-MM-DD"),
    account_code: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    try:
        entries = _ledger(db).list(
            LedgerQuery(
                company_id=company_id,
                status=entry_status,
                date_from=date_from,
                date_to=date_to,
                account_code=account_code,
            )
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return [journal_entry_to_read(entry) for entry in entries]


@router.get("/{entry_id}", response_model=JournalEntryRead)
def get_journal_entry(entry_id: str, db: Session = Depends(get_db)):
    entry = _ledger(db).get(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return journal_entry_to_read(entry)


@router.post("/{entry_id}/approve", response_model=JournalEntryRead)
def approve_journal_entry(entry_id: str, db: Session = Depends(get_db)):
    return _transition(_ledger(db).approve, entry_id)


@router.post("/{entry_id}/post", response_model=JournalEntryRead)
def post_journal_entry(entry_id: str, db: Session = Depends(get_db)):
    return _transition(_ledger(db).post, entry_id)


@router.post("/{entry_id}/reject", response_model=JournalEntryRead)
def reject_journal_entry(entry_id: str, db: Session = Depends(get_db)):
    return _transition(_ledger(db).reject, entry_id)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_journal_entry(entry_id: str, db: Session = Depends(get_db)):
    entry = _ledger(db).get(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    if entry.status == JournalEntryStatus.POSTED.value:
        raise HTTPException(status_code=409, detail="Posted journal entries cannot be deleted")
    JournalRepository(db).delete(entry_id)


def _transition(operation, entry_id: str):
    try:
        return journal_entry_to_read(operation(entry_id))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
