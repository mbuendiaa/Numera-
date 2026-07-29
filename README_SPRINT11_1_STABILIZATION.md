# Numera Sprint 11.1 — Stabilization

Compatible with the existing database. No schema changes or migrations.

- Duplicate invoice detection by company, supplier and invoice number.
- GET /accounting/journal and GET /accounting/journal/{journal_id}.
- Strict journal state transitions.
- Company isolation and role checks on journal operations.
- GET /accounting/statistics.
- Existing ledger and trial balance retained.

Do not replace or delete your existing numera.db.
