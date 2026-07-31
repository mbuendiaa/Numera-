# Sprint 16 — Centro de revisión

## Funcionalidad

- Integración real con `GET /intelligence/review`.
- Métricas de pendientes, baja confianza, OCR, descuadres y duplicados.
- Filtros por tipo de incidencia y buscador.
- Navegación a facturas con incidencias.
- Detalle de asientos contables mediante `GET /journal/{id}`.
- Aprobación y rechazo de asientos propuestos mediante los endpoints del ledger.
- Estados de carga, error, cola vacía y mutaciones.

## Limitaciones actuales del backend

Los documentos OCR pueden revisarse en la cola, pero el backend todavía no expone un endpoint de detalle/edición del documento. La interfaz lo refleja sin simular acciones inexistentes.
