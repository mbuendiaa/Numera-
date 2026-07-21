import json

from sqlalchemy.orm import Session

from numera.domain.accounting.models import ChartAccount, JournalEntry
from numera.domain.schemas import CompanyCreate, InvoiceCreate, SupplierCreate
from numera.infrastructure.persistence.models import (
    AccountORM,
    BusinessEventORM,
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


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def exists_for_company(self, company_id: str) -> bool:
        return self.db.query(AccountORM.id).filter(AccountORM.company_id == company_id).first() is not None

    def get(self, company_id: str, code: str):
        return self.db.query(AccountORM).filter(AccountORM.company_id == company_id, AccountORM.code == code).first()

    def list(self, company_id: str, *, category: str | None = None, active_only: bool = True, search: str | None = None):
        query = self.db.query(AccountORM).filter(AccountORM.company_id == company_id)
        if category:
            query = query.filter(AccountORM.category == category)
        if active_only:
            query = query.filter(AccountORM.is_active.is_(True))
        if search:
            pattern = f"%{search}%"
            query = query.filter((AccountORM.code.ilike(pattern)) | (AccountORM.name.ilike(pattern)))
        return query.order_by(AccountORM.code.asc()).all()

    def upsert(self, company_id: str, account: ChartAccount):
        obj = self.get(company_id, account.code)
        created = obj is None
        if obj is None:
            obj = AccountORM(company_id=company_id, code=account.code)
            self.db.add(obj)
        obj.name = account.name
        obj.group = account.group
        obj.category = account.category
        obj.normal_balance = account.normal_balance
        obj.financial_statement = account.financial_statement
        obj.vat_behavior = account.vat_behavior
        obj.reconcilable = account.reconcilable
        obj.is_active = account.is_active
        self.db.commit()
        self.db.refresh(obj)
        return obj, created


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
        return self.db.query(SupplierORM).filter(SupplierORM.company_id == company_id).filter(SupplierORM.name.ilike(f"%{name}%")).first()


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


class BusinessEventRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _entity_reference(event) -> tuple[str | None, str | None]:
        candidates = (
            ("purchase", "purchase_id"),
            ("invoice", "invoice_id"),
            ("supplier", "supplier_id"),
            ("journal_entry", "journal_entry_id"),
            ("document", "document_id"),
        )
        for entity_type, attribute in candidates:
            value = getattr(event, attribute, None)
            if value:
                return entity_type, value
        source_document_id = getattr(event, "source_document_id", None)
        if source_document_id:
            return "document", source_document_id
        return None, None

    def append(self, event):
        existing = self.db.query(BusinessEventORM).filter(BusinessEventORM.event_id == event.event_id).first()
        if existing:
            return existing
        entity_type, entity_id = self._entity_reference(event)
        obj = BusinessEventORM(
            event_id=event.event_id,
            company_id=event.company_id,
            event_type=event.event_type,
            occurred_at=event.occurred_at,
            entity_type=entity_type,
            entity_id=entity_id,
            payload_json=json.dumps(event.to_dict(), ensure_ascii=False),
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def list(self, *, company_id: str | None = None, event_type: str | None = None, entity_type: str | None = None, entity_id: str | None = None, limit: int = 50):
        query = self.db.query(BusinessEventORM)
        if company_id:
            query = query.filter(BusinessEventORM.company_id == company_id)
        if event_type:
            query = query.filter(BusinessEventORM.event_type == event_type)
        if entity_type:
            query = query.filter(BusinessEventORM.entity_type == entity_type)
        if entity_id:
            query = query.filter(BusinessEventORM.entity_id == entity_id)
        return query.order_by(BusinessEventORM.occurred_at.desc()).limit(limit).all()


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
            lines=[JournalLineORM(position=position, account_code=line.account_code, account_name=line.account_name, description=line.description, debit=line.debit, credit=line.credit) for position, line in enumerate(entry.lines, start=1)],
        )
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj, True

    def get(self, entry_id: str):
        return self.db.query(JournalEntryORM).filter(JournalEntryORM.id == entry_id).first()

    def list(self, company_id: str | None = None, status: str | None = None, date_from: str | None = None, date_to: str | None = None, account_code: str | None = None):
        from numera.engines.ledger.engine import parse_ledger_date
        query = self.db.query(JournalEntryORM)
        if company_id:
            query = query.filter(JournalEntryORM.company_id == company_id)
        if status:
            query = query.filter(JournalEntryORM.status == status)
        if account_code:
            query = query.join(JournalLineORM).filter(JournalLineORM.account_code == account_code).distinct()
        entries = query.order_by(JournalEntryORM.created_at.desc()).all()
        lower = parse_ledger_date(date_from) if date_from else None
        upper = parse_ledger_date(date_to) if date_to else None
        if lower or upper:
            filtered = []
            for entry in entries:
                current = parse_ledger_date(entry.entry_date)
                if lower and current < lower:
                    continue
                if upper and current > upper:
                    continue
                filtered.append(entry)
            entries = filtered
        return sorted(entries, key=lambda entry: parse_ledger_date(entry.entry_date), reverse=True)

    def find_by_document(self, source_document_id: str):
        return self.db.query(JournalEntryORM).filter(JournalEntryORM.source_document_id == source_document_id).first()

    def update_status(self, entry_id: str, status: str):
        entry = self.get(entry_id)
        if entry is None:
            return None
        entry.status = status
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def delete(self, entry_id: str) -> bool:
        entry = self.get(entry_id)
        if entry is None:
            return False
        self.db.delete(entry)
        self.db.commit()
        return True