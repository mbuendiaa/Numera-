# Numera Ledger Engine v1

The Accounting Engine remains responsible for generating balanced journal-entry proposals.
The Ledger Engine is now responsible for persistence, idempotency, querying and lifecycle transitions.

## API

- `GET /journal`
  - filters: `company_id`, `status`, `date_from`, `date_to`, `account_code`
- `GET /journal/{entry_id}`
- `POST /journal/{entry_id}/approve`
- `POST /journal/{entry_id}/post`
- `POST /journal/{entry_id}/reject`
- `DELETE /journal/{entry_id}` (not allowed for posted entries)

Persisted entries remain `proposed` until explicitly approved or posted. Persistence and posting are deliberately separate accounting concepts.
