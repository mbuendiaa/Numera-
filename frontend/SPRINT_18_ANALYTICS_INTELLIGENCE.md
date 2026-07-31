# Sprint 18 — Analytics Intelligence

## Implementado

- KPIs de compras, IVA, ticket medio y tasa de contabilización.
- Evolución mensual de compras e IVA con selector de 6/12 meses.
- Distribución del estado de los asientos contables.
- Ranking de proveedores por volumen comprado.
- Alertas reales de variación de precios.
- Tabla resumen de proveedores.
- Datos obtenidos exclusivamente de endpoints existentes del backend.

## Endpoints utilizados

- `GET /intelligence/dashboard`
- `GET /invoices/`
- `GET /suppliers/`
- `GET /intelligence/suppliers/{id}/analytics`
- `GET /accounting/statistics`
- `GET /products/price-alerts`
