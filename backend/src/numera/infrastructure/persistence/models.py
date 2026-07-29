from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from numera.infrastructure.database.base import Base


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class CompanyORM(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("company"))
    name: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, default="ES")
    currency: Mapped[str] = mapped_column(String, default="EUR")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    suppliers: Mapped[list["SupplierORM"]] = relationship(back_populates="company")
    journal_entries: Mapped[list["JournalEntryORM"]] = relationship(back_populates="company")
    accounts: Mapped[list["AccountORM"]] = relationship(back_populates="company", cascade="all, delete-orphan")


class CompanyMembershipORM(Base):
    __tablename__ = "company_memberships"
    __table_args__ = (UniqueConstraint("user_id", "company_id", name="uq_membership_user_company"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("membership"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String, default="readonly", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String, nullable=True)


class AuditLogORM(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("audit"))
    company_id: Mapped[str | None] = mapped_column(ForeignKey("companies.id"), nullable=True, index=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String, nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    entity_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    details_json: Mapped[str] = mapped_column(Text, default="{}", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("user"))
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    company_id: Mapped[str | None] = mapped_column(ForeignKey("companies.id"), nullable=True, index=True)
    role: Mapped[str] = mapped_column(String, default="owner", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class AuthTokenORM(Base):
    __tablename__ = "auth_tokens"

    jti: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    token_type: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class AccountORM(Base):
    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_account_company_code"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("account"))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    group: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False, index=True)
    normal_balance: Mapped[str] = mapped_column(String, nullable=False)
    financial_statement: Mapped[str] = mapped_column(String, nullable=False, index=True)
    vat_behavior: Mapped[str] = mapped_column(String, default="none", nullable=False)
    reconcilable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    company: Mapped[CompanyORM] = relationship(back_populates="accounts")


class SupplierORM(Base):
    __tablename__ = "suppliers"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("supplier"))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    tax_id: Mapped[str | None] = mapped_column(String, nullable=True)
    country: Mapped[str] = mapped_column(String, default="ES")
    default_account: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    company: Mapped[CompanyORM] = relationship(back_populates="suppliers")


class InvoiceORM(Base):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("invoice"))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    supplier_id: Mapped[str | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    invoice_number: Mapped[str] = mapped_column(String, nullable=False)
    issue_date: Mapped[str] = mapped_column(String, nullable=False)
    base_amount: Mapped[float] = mapped_column(Float, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Float, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, default="received")
    source_document_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CognitiveDecisionORM(Base):
    __tablename__ = "cognitive_decisions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("decision"))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    input_type: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    risk_level: Mapped[str] = mapped_column(String, default="low")
    status: Mapped[str] = mapped_column(String, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DocumentORM(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("document"))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    storage_path: Mapped[str] = mapped_column(String, nullable=False)
    document_type: Mapped[str] = mapped_column(String, default="unknown")
    status: Mapped[str] = mapped_column(String, default="uploaded")
    extracted_text_preview: Mapped[str] = mapped_column(Text, default="")
    extracted_fields_json: Mapped[str] = mapped_column(Text, default="{}")
    created_invoice_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BusinessEventORM(Base):
    __tablename__ = "business_events"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    entity_type: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    entity_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)


class JournalEntryORM(Base):
    __tablename__ = "journal_entries"
    __table_args__ = (
        UniqueConstraint("source_document_id", name="uq_journal_entry_source_document"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("journal"))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    source_event_id: Mapped[str | None] = mapped_column(String, nullable=True)
    source_document_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    entry_date: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String, default="proposed", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    company: Mapped[CompanyORM] = relationship(back_populates="journal_entries")
    lines: Mapped[list["JournalLineORM"]] = relationship(
        back_populates="entry",
        cascade="all, delete-orphan",
        order_by="JournalLineORM.position",
    )

    @property
    def total_debit(self) -> float:
        return round(sum(line.debit for line in self.lines), 2)

    @property
    def total_credit(self) -> float:
        return round(sum(line.credit for line in self.lines), 2)

    @property
    def is_balanced(self) -> bool:
        return abs(self.total_debit - self.total_credit) <= 0.02


class JournalLineORM(Base):
    __tablename__ = "journal_lines"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("journal_line"))
    journal_entry_id: Mapped[str] = mapped_column(
        ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position: Mapped[int] = mapped_column(nullable=False)
    account_code: Mapped[str] = mapped_column(String, nullable=False, index=True)
    account_name: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    debit: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    credit: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    entry: Mapped[JournalEntryORM] = relationship(back_populates="lines")

class TaxRateORM(Base):
    __tablename__ = "tax_rates"
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_tax_company_code"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("tax"))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(7, 4), nullable=False, default=0)
    surcharge_rate: Mapped[float] = mapped_column(Numeric(7, 4), nullable=False, default=0)
    scope: Mapped[str] = mapped_column(String, nullable=False, default="domestic")
    kind: Mapped[str] = mapped_column(String, nullable=False, default="vat")
    deductible_percent: Mapped[float] = mapped_column(Numeric(7, 4), nullable=False, default=100)
    is_exempt: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reverse_charge: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class TaxDocumentORM(Base):
    __tablename__ = "tax_documents"
    __table_args__ = (UniqueConstraint("company_id", "document_type", "number", name="uq_tax_document_number"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("taxdoc"))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    number: Mapped[str] = mapped_column(String, nullable=False, index=True)
    counterparty_name: Mapped[str] = mapped_column(String, nullable=False)
    counterparty_tax_id: Mapped[str | None] = mapped_column(String, nullable=True)
    issue_date: Mapped[str] = mapped_column(String, nullable=False, index=True)
    due_date: Mapped[str | None] = mapped_column(String, nullable=True)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="EUR")
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")
    subtotal: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False, default=0)
    discount_total: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False, default=0)
    tax_total: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False, default=0)
    surcharge_total: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False, default=0)
    total: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False, default=0)
    source_document_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class TaxDocumentLineORM(Base):
    __tablename__ = "tax_document_lines"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("taxline"))
    document_id: Mapped[str] = mapped_column(ForeignKey("tax_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(16, 4), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(16, 4), nullable=False)
    discount_percent: Mapped[float] = mapped_column(Numeric(7, 4), nullable=False, default=0)
    tax_rate_id: Mapped[str] = mapped_column(ForeignKey("tax_rates.id"), nullable=False, index=True)
    account_code: Mapped[str | None] = mapped_column(String, nullable=True)
    base_amount: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False)
    surcharge_amount: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False)


class VATSettlementORM(Base):
    __tablename__ = "vat_settlements"
    __table_args__ = (UniqueConstraint("company_id", "period_start", "period_end", name="uq_vat_period"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("vatset"))
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    period_start: Mapped[str] = mapped_column(String, nullable=False, index=True)
    period_end: Mapped[str] = mapped_column(String, nullable=False, index=True)
    output_base: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False, default=0)
    output_vat: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False, default=0)
    input_base: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False, default=0)
    input_vat: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False, default=0)
    deductible_input_vat: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False, default=0)
    vat_due: Mapped[float] = mapped_column(Numeric(16, 2), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String, nullable=False, default="draft")
    created_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
