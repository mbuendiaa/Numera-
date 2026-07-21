# Numera Document to Accounting v0.8 Patch

This patch connects:

```text
Document Engine
    ↓
Created Invoice
    ↓
AccountingEvent
    ↓
AccountingEngine
    ↓
Proposed Journal Entry
```

## Files to replace/add

```text
backend/src/numera/domain/accounting_mapper.py
backend/src/numera/domain/document_service.py
backend/src/numera/domain/schemas.py
backend/src/numera/api/routes/documents.py
backend/tests/test_accounting_mapper.py
```

## Test

From backend:

```cmd
pytest
```

## Run

```cmd
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
uvicorn numera.main:app --reload --reload-dir src
```

## Expected Swagger result

When uploading a valid invoice PDF, response should include:

```text
created_invoice
proposed_journal_entry
```

Example journal entry:

```text
Debit  600000 Purchases       309.60
Debit  472000 Input VAT        30.96
Credit 400000 Suppliers       340.56
```

No database deletion required.
