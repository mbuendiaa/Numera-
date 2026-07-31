# Sprint 19 — Settings & Company Administration

## Funcionalidad incluida

- Vista de empresa activa y cambio entre empresas disponibles.
- Administración real de miembros mediante los endpoints multitenant existentes.
- Alta de usuarios registrados, actualización de roles y eliminación de accesos.
- Preferencias contables persistidas localmente hasta que el backend exponga endpoints dedicados.
- Preferencias de apariencia, idioma, zona horaria, OCR y notificaciones.
- Registro de auditoría de la empresa.
- Estados de carga, error, confirmación y permisos por rol.

## Endpoints utilizados

- `GET /auth/me`
- `GET /companies/my`
- `POST /companies/{company_id}/activate`
- `GET /companies/{company_id}/members`
- `POST /companies/{company_id}/members`
- `PATCH /companies/{company_id}/members/{user_id}`
- `DELETE /companies/{company_id}/members/{user_id}`
- `GET /companies/{company_id}/audit`
