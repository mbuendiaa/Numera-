# PR #9 — Purchase API

This change exposes the Purchase application layer through FastAPI while keeping
the domain independent from HTTP concerns.

## Endpoints

- `POST /purchases`
- `GET /purchases`
- `GET /purchases/{purchase_id}`
- `POST /purchases/{purchase_id}/approve`
- `POST /purchases/{purchase_id}/payments`

## Run

```bash
cd backend
python -m pip install -e ".[dev]"
uvicorn numera.main:app --reload
```

Swagger UI: `http://localhost:8000/docs`

## Validate

```bash
cd backend
pytest
```

Validated in the supplied project: **63 tests passed**.
