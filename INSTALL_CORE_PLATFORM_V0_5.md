# Install Numera Core Platform v0.5 Stable

This version adds:

- OCR support through Tesseract.
- Invoice Extraction Engine.
- Extraction of supplier, invoice number, date, base, VAT and total.
- Automatic invoice creation when total amount is found.
- `created_invoice` returned in `/documents/upload`.

## 1. Stop the server

```cmd
CTRL + C
```

## 2. Backup your current backend

Rename your current folder:

```text
backend
```

to:

```text
backend_backup_v0_4
```

## 3. Copy the new backend

Copy the `backend` folder from this ZIP into your Numera repository.

## 4. Activate environment

```cmd
cd C:\Users\marta\OneDrive\Documentos\GitHub\Numera-\backend
.venv\Scripts\activate
```

If `.venv` does not exist:

```cmd
py -m venv .venv
.venv\Scripts\activate
```

## 5. Install dependencies

```cmd
py -m pip install -e .[dev]
```

## 6. Configure Tesseract

```cmd
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

## 7. Reset local database

Because the database schema changed, delete:

```text
backend\numera.db
```

Then it will be recreated automatically.

## 8. Run server

```cmd
uvicorn numera.main:app --reload --reload-dir src
```

## 9. Open Swagger

```text
http://127.0.0.1:8000/docs
```

## 10. Test

Create a company, then use:

```text
POST /documents/upload
```

Upload the invoice JPG again.

Expected result:

- `detected_type = invoice`
- `extracted_fields`
- maybe `created_invoice` if Numera finds the total amount.
