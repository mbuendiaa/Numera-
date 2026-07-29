# Journal Engine v1.0

## Added

- `journal_entries` and `journal_lines` persistence
- `JournalRepository`
- automatic persistence after invoice accounting generation
- idempotency by `source_document_id`
- `GET /journal?company_id=...`
- `GET /journal/{entry_id}`
- repository tests

## Run

```cmd
cd backend
.venv\Scripts\activate
pytest
uvicorn numera.main:app --reload
```

Existing SQLite databases are extended automatically through `Base.metadata.create_all`.
