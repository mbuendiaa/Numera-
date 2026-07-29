# Numera Sprint 11 — Accounting Engine

This sprint turns accounting proposals into an operational accounting ledger.

## New API

- `POST /accounting/journal` — create a validated manual journal proposal.
- `GET /accounting/ledger/{account_code}` — general ledger movements and running balance.
- `GET /accounting/trial-balance` — trial balance by period and journal status.
- `GET /accounting/journal-summary` — counts and posted totals by lifecycle status.

## Accounting controls

- Every manual entry must contain at least two lines.
- A line cannot have debit and credit simultaneously.
- Entries must balance before they are recorded.
- Account codes must exist and be active in the selected company.
- Ledger and trial balance are isolated by the authenticated user's active company.
- Posted entries are used by default for official ledger balances.
- A default operational subset of the Spanish PGC is seeded automatically when a company is created.

## Existing lifecycle

The existing journal endpoints remain available to approve, post or reject proposals:

- `POST /journal/{entry_id}/approve`
- `POST /journal/{entry_id}/post`
- `POST /journal/{entry_id}/reject`

## Database safety

The ZIP intentionally excludes `numera.db` and uploaded documents. Preserve your existing database while replacing the application code.
