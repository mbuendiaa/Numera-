from pydantic import BaseModel, Field, model_validator


class ManualJournalLineCreate(BaseModel):
    account_code: str = Field(..., min_length=3, max_length=12, pattern=r"^[0-9]+$")
    description: str = ""
    debit: float = Field(default=0, ge=0)
    credit: float = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_side(self):
        if self.debit > 0 and self.credit > 0:
            raise ValueError("A journal line cannot contain both debit and credit.")
        if self.debit == 0 and self.credit == 0:
            raise ValueError("A journal line must contain a debit or a credit amount.")
        return self


class ManualJournalEntryCreate(BaseModel):
    entry_date: str = Field(..., description="DD/MM/YYYY or YYYY-MM-DD")
    description: str = Field(..., min_length=1)
    lines: list[ManualJournalLineCreate] = Field(..., min_length=2)


class LedgerMovementRead(BaseModel):
    journal_entry_id: str
    entry_date: str
    entry_description: str
    line_description: str
    debit: float
    credit: float
    running_balance: float


class AccountLedgerRead(BaseModel):
    company_id: str
    account_code: str
    account_name: str
    normal_balance: str
    opening_balance: float
    total_debit: float
    total_credit: float
    closing_balance: float
    movements: list[LedgerMovementRead]


class TrialBalanceLineRead(BaseModel):
    account_code: str
    account_name: str
    category: str
    total_debit: float
    total_credit: float
    balance: float


class TrialBalanceRead(BaseModel):
    company_id: str
    date_from: str | None = None
    date_to: str | None = None
    status: str
    lines: list[TrialBalanceLineRead]
    total_debit: float
    total_credit: float
    is_balanced: bool


class JournalSummaryRead(BaseModel):
    company_id: str
    proposed: int
    approved: int
    posted: int
    rejected: int
    total_entries: int
    posted_debit: float
    posted_credit: float
