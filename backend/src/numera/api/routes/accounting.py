from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from numera.api.dependencies import get_active_membership, require_company_roles
from numera.api.schemas.accounting import (
    AccountLedgerRead,
    JournalSummaryRead,
    LedgerMovementRead,
    ManualJournalEntryCreate,
    TrialBalanceLineRead,
    TrialBalanceRead,
)
from numera.api.serializers import journal_entry_to_read
from numera.domain.accounting.models import AccountingEventType, JournalEntry, JournalEntryStatus, JournalLine
from numera.domain.schemas import JournalEntryRead
from numera.engines.ledger.engine import LedgerEngine, parse_ledger_date
from numera.infrastructure.database.session import get_db
from numera.infrastructure.persistence.models import AccountORM, JournalEntryORM, JournalLineORM
from numera.infrastructure.repositories import JournalRepository

router = APIRouter()


def _date_in_range(value: str, date_from: str | None, date_to: str | None) -> bool:
    current = parse_ledger_date(value)
    if date_from and current < parse_ledger_date(date_from):
        return False
    if date_to and current > parse_ledger_date(date_to):
        return False
    return True


def _active_company_id(membership) -> str:
    return membership.company_id


@router.post("/journal", response_model=JournalEntryRead, status_code=status.HTTP_201_CREATED)
def create_manual_journal_entry(
    payload: ManualJournalEntryCreate,
    membership=Depends(require_company_roles("owner", "admin", "accountant")),
    db: Session = Depends(get_db),
):
    company_id = _active_company_id(membership)
    try:
        parse_ledger_date(payload.entry_date)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    codes = {line.account_code for line in payload.lines}
    accounts = (
        db.query(AccountORM)
        .filter(AccountORM.company_id == company_id, AccountORM.code.in_(codes), AccountORM.is_active.is_(True))
        .all()
    )
    account_map = {account.code: account for account in accounts}
    missing = sorted(codes - set(account_map))
    if missing:
        raise HTTPException(status_code=422, detail=f"Unknown or inactive account(s): {', '.join(missing)}")

    lines = [
        JournalLine(
            account_code=line.account_code,
            account_name=account_map[line.account_code].name,
            description=line.description or payload.description,
            debit=round(line.debit, 2),
            credit=round(line.credit, 2),
        )
        for line in payload.lines
    ]
    entry = JournalEntry(
        company_id=company_id,
        event_type=AccountingEventType.MANUAL_ADJUSTMENT,
        entry_date=payload.entry_date,
        description=payload.description,
        lines=lines,
        status=JournalEntryStatus.PROPOSED,
    )
    if not entry.is_balanced:
        raise HTTPException(status_code=422, detail="Journal entry is not balanced.")
    obj, _ = LedgerEngine(JournalRepository(db)).record(entry)
    return journal_entry_to_read(obj)


@router.get("/ledger/{account_code}", response_model=AccountLedgerRead)
def account_ledger(
    account_code: str,
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    include_unposted: bool = Query(default=False),
    membership=Depends(get_active_membership),
    db: Session = Depends(get_db),
):
    company_id = _active_company_id(membership)
    account = db.query(AccountORM).filter(AccountORM.company_id == company_id, AccountORM.code == account_code).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    try:
        if date_from:
            parse_ledger_date(date_from)
        if date_to:
            parse_ledger_date(date_to)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    query = (
        db.query(JournalEntryORM, JournalLineORM)
        .join(JournalLineORM, JournalLineORM.journal_entry_id == JournalEntryORM.id)
        .filter(JournalEntryORM.company_id == company_id, JournalLineORM.account_code == account_code)
    )
    if not include_unposted:
        query = query.filter(JournalEntryORM.status == JournalEntryStatus.POSTED.value)
    rows = query.all()
    rows = [(entry, line) for entry, line in rows if _date_in_range(entry.entry_date, date_from, date_to)]
    rows.sort(key=lambda row: (parse_ledger_date(row[0].entry_date), row[1].position))

    running = 0.0
    movements = []
    total_debit = total_credit = 0.0
    for entry, line in rows:
        debit, credit = round(float(line.debit), 2), round(float(line.credit), 2)
        total_debit += debit
        total_credit += credit
        delta = debit - credit if account.normal_balance == "debit" else credit - debit
        running = round(running + delta, 2)
        movements.append(LedgerMovementRead(
            journal_entry_id=entry.id,
            entry_date=entry.entry_date,
            entry_description=entry.description,
            line_description=line.description,
            debit=debit,
            credit=credit,
            running_balance=running,
        ))
    return AccountLedgerRead(
        company_id=company_id,
        account_code=account.code,
        account_name=account.name,
        normal_balance=account.normal_balance,
        opening_balance=0,
        total_debit=round(total_debit, 2),
        total_credit=round(total_credit, 2),
        closing_balance=running,
        movements=movements,
    )


@router.get("/trial-balance", response_model=TrialBalanceRead)
def trial_balance(
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    entry_status: JournalEntryStatus = Query(default=JournalEntryStatus.POSTED, alias="status"),
    membership=Depends(get_active_membership),
    db: Session = Depends(get_db),
):
    company_id = _active_company_id(membership)
    try:
        if date_from:
            parse_ledger_date(date_from)
        if date_to:
            parse_ledger_date(date_to)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    entries = (
        db.query(JournalEntryORM)
        .options(joinedload(JournalEntryORM.lines))
        .filter(JournalEntryORM.company_id == company_id, JournalEntryORM.status == entry_status.value)
        .all()
    )
    entries = [entry for entry in entries if _date_in_range(entry.entry_date, date_from, date_to)]
    accounts = {a.code: a for a in db.query(AccountORM).filter(AccountORM.company_id == company_id).all()}
    totals: dict[str, list[float]] = {}
    for entry in entries:
        for line in entry.lines:
            bucket = totals.setdefault(line.account_code, [0.0, 0.0])
            bucket[0] += float(line.debit)
            bucket[1] += float(line.credit)

    lines = []
    for code in sorted(totals):
        debit, credit = [round(value, 2) for value in totals[code]]
        account = accounts.get(code)
        lines.append(TrialBalanceLineRead(
            account_code=code,
            account_name=account.name if account else (next((l.account_name for e in entries for l in e.lines if l.account_code == code), None) or code),
            category=account.category if account else "unknown",
            total_debit=debit,
            total_credit=credit,
            balance=round(debit - credit, 2),
        ))
    total_debit = round(sum(line.total_debit for line in lines), 2)
    total_credit = round(sum(line.total_credit for line in lines), 2)
    return TrialBalanceRead(
        company_id=company_id,
        date_from=date_from,
        date_to=date_to,
        status=entry_status.value,
        lines=lines,
        total_debit=total_debit,
        total_credit=total_credit,
        is_balanced=abs(total_debit - total_credit) <= 0.02,
    )


@router.get("/journal-summary", response_model=JournalSummaryRead)
def journal_summary(
    membership=Depends(get_active_membership),
    db: Session = Depends(get_db),
):
    company_id = _active_company_id(membership)
    entries = db.query(JournalEntryORM).filter(JournalEntryORM.company_id == company_id).all()
    counts = {value: 0 for value in ("proposed", "approved", "posted", "rejected")}
    posted_debit = posted_credit = 0.0
    for entry in entries:
        counts[entry.status] = counts.get(entry.status, 0) + 1
        if entry.status == "posted":
            posted_debit += entry.total_debit
            posted_credit += entry.total_credit
    return JournalSummaryRead(
        company_id=company_id,
        proposed=counts["proposed"], approved=counts["approved"], posted=counts["posted"], rejected=counts["rejected"],
        total_entries=len(entries), posted_debit=round(posted_debit, 2), posted_credit=round(posted_credit, 2),
    )
