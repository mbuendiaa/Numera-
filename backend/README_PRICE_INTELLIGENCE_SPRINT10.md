# Numera Sprint 10 — Price Intelligence

This release adds price evolution, supplier comparison and automatic price alerts on top of invoice ingestion.

## New endpoints

- `GET /products/{product_id}/price-analysis`
  - first, previous and latest price
  - min, max, average and quantity-weighted average
  - absolute and percentage change
  - trend (`up`, `down`, `stable`, `insufficient_data`)
  - optional supplier and date filters

- `GET /products/{product_id}/supplier-comparison`
  - latest/min/max/average by supplier
  - best current supplier
  - absolute and percentage difference from the best price
  - optional date filters

- `GET /products/price-alerts`
  - detects increases/decreases against the preceding observation for each supplier product
  - configurable percentage threshold and direction

Invoice uploads continue to populate the supplier-product catalogue and price history automatically.

## Database preservation

This ZIP intentionally does not include `numera.db`. When updating an existing installation, keep the existing `backend/numera.db` file so users, companies, invoices and uploaded price history are preserved.

## Validation

`74 passed`
