# Numera Core Platform v0.1

Initial backend foundation for Numera.

## Stack

- FastAPI
- Pydantic
- SQLAlchemy-ready structure
- Clean Architecture style
- Domain modules prepared for the Cognitive System

## Run locally

```cmd
cd backend
py -m venv .venv
.venv\Scripts\activate
py -m pip install -e .[dev]
uvicorn numera.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```
