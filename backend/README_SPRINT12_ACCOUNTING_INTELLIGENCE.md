# Numera Sprint 12 — Accounting Intelligence

This sprint adds read-only intelligence and analytics without changing the database schema.

## New endpoints

- `GET /intelligence/classify/invoice/{invoice_id}`
- `GET /intelligence/review`
- `GET /intelligence/dashboard`
- `GET /intelligence/suppliers/{supplier_id}/analytics`
- `GET /intelligence/products/{product_id}/analytics`

## Compatibility

- No migrations.
- No new tables or columns.
- Existing `numera.db` remains compatible.
- Existing IDs, uploads and API routes are preserved.

The classification engine uses supplier defaults, supplier rules, keyword rules and a safe default purchase account. Low-confidence classifications are surfaced in the review center.
