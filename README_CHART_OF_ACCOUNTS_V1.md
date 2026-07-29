# Numera Chart of Accounts Engine v1

This version introduces a persistent, company-specific chart of accounts.

## API

- `GET /accounts?company_id=...`
- `GET /accounts/{code}?company_id=...`
- `POST /accounts?company_id=...`
- `POST /accounts/seed?company_id=...`

The first account query or invoice posting automatically seeds an operational subset of the Spanish PGC. Seeding is idempotent.

The Accounting Engine now resolves accounts 600000, 472000 and 400000 from the persistent chart instead of embedding account names in the posting logic.
