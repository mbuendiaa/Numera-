# Numera Sprint 8 — Product Master and supplier price comparison

This sprint adds a company-scoped product master, supplier catalog links and historical price observations.

## Data model

- `products`: internal product identity shared across suppliers.
- `supplier_products`: a supplier-specific reference and description linked to the internal product.
- `product_price_history`: immutable price observations extracted from invoices or entered manually.

A product can therefore be sold by several suppliers with different references and prices.

## Main API flow

1. `POST /products/` creates the internal product.
2. `POST /products/suppliers/{supplier_id}` links the supplier reference.
3. `POST /products/supplier-products/{supplier_product_id}/prices` records an invoice price.
4. `GET /products/{product_id}/supplier-offers` compares the latest supplier prices.
5. `GET /products/{product_id}/price-history` returns the historical series.
6. `GET /products/suppliers/{supplier_id}/catalog` displays all products below a supplier.

All routes use the authenticated user's active company. Company IDs are intentionally not accepted in request bodies.
