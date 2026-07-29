# Numera Frontend — Sprint F2

Frontend conectado al backend real de Numera.

## Novedades

- Login real contra `POST /auth/login`
- JWT guardado localmente
- Protección de rutas
- Cierre de sesión
- Proxy interno de Next.js para evitar problemas CORS
- Dashboard real contra `GET /intelligence/dashboard`
- Listado real contra `GET /invoices/`
- Subida PDF contra `POST /documents/upload`
- Detección visual de duplicados
- Detalle de factura con documento y campos OCR
- Estados de carga y errores de conexión
- Eliminación de los datos inventados del dashboard

## Requisitos

- Node.js 20 o superior
- Backend Sprint 12 activo
- Un usuario registrado y una empresa activa en Numera

## Instalación en Windows CMD

```cmd
copy .env.example .env.local
npm install
npm run dev
```

Abre:

```text
http://localhost:3000
```

## Arrancar el backend

El frontend espera FastAPI en:

```text
http://localhost:8000
```

Configurable en `.env.local`:

```env
NUMERA_BACKEND_URL=http://localhost:8000
```

Debes arrancar el backend por separado. Usa el mismo comando con el que venías abriendo Swagger.

## Probar

1. Arranca FastAPI.
2. Arranca el frontend con `npm run dev`.
3. Entra en `http://localhost:3000`.
4. Identifícate con el usuario real del backend.
5. Abre Facturas.
6. Arrastra un PDF.
7. Espera a que termine el procesamiento.
8. Comprueba el listado y el detalle.

## Nota sobre el detalle

El backend actual no tiene `GET /invoices/{id}`. Para mantener compatibilidad sin cambiar la base de datos, el frontend obtiene el listado y localiza la factura por ID. En un próximo sprint conviene añadir ese endpoint al backend.
