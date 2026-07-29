# Numera Sprint 6 — Multiempresa, roles y auditoría

## Flujo en Swagger

1. Registra o inicia sesión en `/auth`.
2. Pulsa **Authorize**.
3. Crea una empresa con `POST /companies/`.
4. Consulta tus empresas con `GET /companies/my`.
5. Añade usuarios ya registrados con `POST /companies/{company_id}/members`.
6. El usuario selecciona empresa activa con `POST /companies/{company_id}/activate`.
7. Consulta el historial en `GET /companies/{company_id}/audit`.

Los roles se asignan por empresa: owner, admin, accountant, manager, employee y readonly.
