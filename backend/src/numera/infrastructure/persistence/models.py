from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
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
