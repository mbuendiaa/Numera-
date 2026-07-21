# Install Numera Core Platform v0.4

This version adds OCR for images and first invoice field extraction.

## Important

Python packages are installed automatically, but Windows also needs the Tesseract program.

Install Tesseract for Windows:
https://github.com/UB-Mannheim/tesseract/wiki

During installation, include Spanish language data if possible.

If Tesseract is installed in the default path, add this environment variable before running:

```cmd
set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

If it still does not work, edit:

```text
backend/src/numera/core/config.py
```

and set:

```python
tesseract_cmd: str | None = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```

## Install

1. Stop the server with `CTRL + C`.

2. Replace your old `backend` folder with this new `backend` folder.

3. Run:

```cmd
cd backend
.venv\Scripts\activate
py -m pip install -e .[dev]
uvicorn numera.main:app --reload --reload-dir src
```

4. Open:

```text
http://127.0.0.1:8000/docs
```

5. Test:

```text
POST /documents/upload
```

Upload a JPG/PNG/PDF.
