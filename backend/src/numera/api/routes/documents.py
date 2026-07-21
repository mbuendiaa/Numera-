from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from numera.api.serializers import journal_entry_to_read
from numera.domain.document_service import DocumentService
from numera.domain.schemas import (
    DocumentRead,
    DocumentUploadResponse,
    InvoiceRead,
)
from numera.infrastructure.database.session import get_db
from numera.infrastructure.repositories import DocumentRepository

router = APIRouter()



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
        proposed_journal_entry=journal_entry_to_read(proposed_entry),
    )


@router.get("/", response_model=list[DocumentRead])
def list_documents(db: Session = Depends(get_db)):
    return DocumentRepository(db).list()
