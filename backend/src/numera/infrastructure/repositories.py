from sqlalchemy.orm import Session

from numera.domain.schemas import CompanyCreate, InvoiceCreate, SupplierCreate
from numera.infrastructure.persistence.models import (
    CognitiveDecisionORM,
    CompanyORM,
    DocumentORM,
    InvoiceORM,
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
