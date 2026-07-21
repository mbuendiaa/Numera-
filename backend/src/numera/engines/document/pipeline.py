from pathlib import Path

from fastapi import UploadFile

from numera.core.config import settings
from numera.engines.document.classifier import DocumentClassifier
from numera.engines.document.extractor import InvoiceExtractor
from numera.engines.document.loader import DocumentLoader
from numera.engines.document.ocr import TextExtractor


class DocumentPipeline:
    def __init__(self):
        self.loader = DocumentLoader()
        self.extractor = TextExtractor()
        self.classifier = DocumentClassifier()
        self.invoice_extractor = InvoiceExtractor()

    def run(self, *, company_id: str, file: UploadFile) -> dict:
        stored_path = self.loader.save_upload(
            upload_dir=Path(settings.upload_dir),
            company_id=company_id,
            file=file,
        )

        text, extraction_explanation = self.extractor.extract_text(stored_path, file.content_type or "")
        document_type, classification_explanation = self.classifier.classify(text, file.filename)

        fields = {}
        parser_explanation = []

        if document_type == "invoice" and not text.startswith("OCR_ERROR"):
            fields, parser_explanation = self.invoice_extractor.extract(text)

        return {
            "storage_path": str(stored_path),
            "document_type": document_type,
            "text_preview": text[:1500],
            "extracted_fields": fields,
            "explanation": extraction_explanation + classification_explanation + parser_explanation,
        }
