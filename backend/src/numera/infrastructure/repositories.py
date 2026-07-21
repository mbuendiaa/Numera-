from sqlalchemy.orm import Session

from numera.domain.accounting.models import JournalEntry
from numera.domain.schemas import CompanyCreate, InvoiceCreate, SupplierCreate
from numera.infrastructure.persistence.models import (
    CognitiveDecisionORM,
    CompanyORM,
    DocumentORM,
    InvoiceORM,
    JournalEntryORM,
    JournalLineORM,
    SupplierORM,
)


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: CompanyCreate):
        obj = CompanyORM(**payload.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list(self):
        return self.db.query(CompanyORM).order_by(CompanyORM.created_at.desc()).all()


class SupplierRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: SupplierCreate):
        obj = SupplierORM(**payload.model_dump())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list(self):
        return self.db.query(SupplierORM).order_by(SupplierORM.created_at.desc()).all()

    def find_by_name(self, company_id: str, name: str):
        return (
            self.db.query(SupplierORM)
            .filter(SupplierORM.company_id == company_id)
            .filter(SupplierORM.name.ilike(f"%{name}%"))
            .first()
        )


class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: InvoiceCreate, source_document_id: str | None = None):
        obj = InvoiceORM(**payload.model_dump(), source_document_id=source_document_id)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list(self):
        return self.db.query(InvoiceORM).order_by(InvoiceORM.created_at.desc()).all()


class CognitiveDecisionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs):
        kwargs["explanation"] = "\n".join(kwargs["explanation"])
        obj = CognitiveDecisionORM(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list(self):
        return self.db.query(CognitiveDecisionORM).order_by(CognitiveDecisionORM.created_at.desc()).all()


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs):
        obj = DocumentORM(**kwargs)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def set_created_invoice(self, document_id: str, invoice_id: str):
        obj = self.db.query(DocumentORM).filter(DocumentORM.id == document_id).first()
        if obj:
            obj.created_invoice_id = invoice_id
            self.db.commit()
            self.db.refresh(obj)
        return obj

    def list(self):
        return self.db.query(DocumentORM).order_by(DocumentORM.created_at.desc()).all()


class JournalRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, entry: JournalEntry):
        if entry.source_document_id:
            existing = self.find_by_document(entry.source_document_id)
            if existing:
                return existing, False

        obj = JournalEntryORM(
            company_id=entry.company_id,
            event_type=entry.event_type.value,
            source_event_id=entry.source_event_id,
            source_document_id=entry.source_document_id,
            entry_date=entry.entry_date,
            description=entry.description,
            status=entry.status.value,
            lines=[
                JournalLineORM(
                    position=position,
                    account_code=line.account_code,
                    account_name=line.account_name,
                    description=line.description,
                    debit=line.debit,
                    credit=line.credit,
                )
                for position, line in enumerate(entry.lines, start=1)
            ],
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj, True

    def get(self, entry_id: str):
        return self.db.query(JournalEntryORM).filter(JournalEntryORM.id == entry_id).first()

    def list(self, company_id: str | None = None):
        query = self.db.query(JournalEntryORM)
        if company_id:
            query = query.filter(JournalEntryORM.company_id == company_id)
        return query.order_by(JournalEntryORM.entry_date.desc(), JournalEntryORM.created_at.desc()).all()

    def find_by_document(self, source_document_id: str):
        return (
            self.db.query(JournalEntryORM)
            .filter(JournalEntryORM.source_document_id == source_document_id)
            .first()
        )
