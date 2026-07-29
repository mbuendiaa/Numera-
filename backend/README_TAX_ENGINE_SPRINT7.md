# Sprint 7 — Motor fiscal y de IVA

Añade un libro fiscal multiempresa con tipos configurables, facturas emitidas/recibidas por líneas, cálculo monetario con `Decimal`, notas de crédito, inversión del sujeto pasivo, recargo de equivalencia, resumen de IVA y liquidaciones.

Flujo Swagger:
1. Autorizarse y seleccionar empresa activa.
2. `POST /tax/rates/seed`.
3. Consultar `GET /tax/rates` y copiar IDs.
4. Crear facturas con `POST /tax/documents`.
5. Consultar `GET /tax/vat/summary`.
6. Cerrar borrador con `POST /tax/vat/settlements`.

Este módulo ayuda a preparar la contabilidad, pero la presentación oficial ante la AEAT debe validarse con asesoría fiscal y adaptarse a los datos censales de cada empresa.
