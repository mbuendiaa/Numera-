# Sprint 15 — Supplier Intelligence Frontend

## Incluido

- Sustitución de la pantalla placeholder de Proveedores.
- Directorio conectado a `/suppliers/`.
- Métricas agregadas mediante `/intelligence/suppliers/{id}/analytics`.
- Buscador por nombre, NIF y cuenta contable.
- Ficha individual de proveedor en `/suppliers/{id}`.
- Catálogo real mediante `/products/suppliers/{id}/catalog`.
- Histórico de facturas filtrado por proveedor.
- Estados de carga, error, vacío y sin resultados.
- Navegación desde proveedor a factura.

## Validación

- TypeScript validado con `tsc --noEmit`.
- El build completo de Next.js no pudo ejecutarse en el entorno de empaquetado porque el binario SWC de Next no estaba disponible localmente y su descarga devolvió 404.
