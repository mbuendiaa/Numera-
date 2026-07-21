from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from numera.api.routes.documents import _journal_entry_to_read
from numera.domain.schemas import JournalEntryRead
from numera.infrastructure.database.session import get_db
from numera.infrastructure.repositories import JournalRepository

router = APIRouter()


@router.get("/", response_model=list[JournalEntryRead])
def list_journal_entries(
    company_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return [_journal_entry_to_read(entry) for entry in JournalRepository(db).list(company_id)]


@router.get("/{entry_id}", response_model=JournalEntryRead)
def get_journal_entry(entry_id: str, db: Session = Depends(get_db)):
    entry = JournalRepository(db).get(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    return _journal_entry_to_read(entry)
