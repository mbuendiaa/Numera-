from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from numera.domain.document_service import DocumentService
from numera.domain.schemas import (
    DocumentRead,
    DocumentUploadResponse,
    InvoiceRead,
    JournalEntryRead,
    JournalLineRead,
)
from numera.infrastructure.database.session import get_db
from numera.infrastructure.repositories import DocumentRepository

router = APIRouter()


def _journal_entry_to_read(entry):
    if entry is None:
        return None

    return JournalEntryRead(
        company_id=entry.company_id,
        event_type=entry.event_type.value,
        source_event_id=entry.source_event_id,
        source_document_id=entry.source_document_id,
        entry_date=entry.entry_date,
        description=entry.description,
        status=entry.status.value,
        lines=[
            JournalLineRead(
                account_code=line.account_code,
                account_name=line.account_name,
                description=line.description,
                debit=line.debit,
                credit=line.credit,
            )
            for line in entry.lines
        ],
        total_debit=entry.total_debit,
        total_credit=entry.total_credit,
        is_balanced=entry.is_balanced,
    )


@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(
    company_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    document, result, created_invoice, proposed_entry = DocumentService(db).upload_and_process(
        company_id=company_id,
        file=file,
    )

    return DocumentUploadResponse(
        document=DocumentRead.model_validate(document),
        pipeline_status="completed",
        detected_type=result["document_type"],
        explanation=result["explanation"],
        extracted_fields=result["extracted_fields"],
        created_invoice=InvoiceRead.model_validate(created_invoice) if created_invoice else None,
        proposed_journal_entry=_journal_entry_to_read(proposed_entry),
    )


@router.get("/", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)):
    return DocumentRepository(db).list()
