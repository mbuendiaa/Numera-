# Sprint 9 — Invoice ingestion and automatic catalog

`POST /documents/upload` now uses the authenticated user's active company and accepts only the invoice file.
It extracts header data, VAT, payment data and product lines. When a supplier and line are resolved, Numera automatically creates/reuses the internal product, links the supplier reference and records the observed price.

The accounting entry remains proposed; this sprint focuses on document ingestion and master-data learning.
