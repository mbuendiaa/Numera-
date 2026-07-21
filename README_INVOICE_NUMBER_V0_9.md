# Numera Invoice Number v0.9 Patch

Improves invoice number extraction with candidate scoring.

## Replace

```text
backend/src/numera/engines/document/patterns.py
backend/src/numera/engines/document/extractor.py
```

## Add

```text
backend/tests/test_invoice_number_extraction.py
```

## Test

```cmd
cd backend
.venv\Scripts\activate
pytest
```

Expected extraction:

```text
V1/2604047
```

instead of:

```text
A1/437142
```

No database deletion required.
