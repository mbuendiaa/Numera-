# Numera Frontend — Sprint F1

Frontend inicial de Numera construido con Next.js, React, TypeScript y Tailwind CSS.

## Incluye

- Login de demostración
- Layout responsive
- Sidebar
- Topbar
- Selector de empresa
- Tema claro/oscuro
- Dashboard con métricas, gráfica, alertas y últimas facturas
- Rutas preparadas para facturas, productos, proveedores, contabilidad, revisión, analytics y configuración
- Cliente API base en `lib/api.ts`
- React Query configurado

## Requisitos

- Node.js 20 o superior
- npm 10 o superior

## Arranque

```bash
npm install
cp .env.example .env.local
npm run dev
```

Abre:

```text
http://localhost:3000
```

La raíz redirige a `/dashboard`.

Para ver el login:

```text
http://localhost:3000/login
```

El login es una demo local y no valida credenciales todavía.

## Backend

Por defecto, el frontend espera el backend FastAPI en:

```text
http://localhost:8000
```

Puedes cambiarlo en `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Siguiente sprint

Sprint F2:

- autenticación real;
- subida de facturas PDF;
- listado de facturas;
- detalle de factura;
- estado OCR;
- conexión con los endpoints reales del backend.
