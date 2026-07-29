# Numera Frontend — Sprint F2.1

Flujo comercial completo de alta, acceso y creación de empresa.

## Qué corrige

- El frontend usa `http://127.0.0.1:8000` en vez de `localhost:8000`.
  En Windows, `localhost` podía resolverse por IPv6 mientras Uvicorn estaba escuchando en IPv4.
- Ya no es necesario abrir Swagger para crear usuarios.
- Un usuario sin empresa es enviado automáticamente al onboarding.
- Al crear la empresa, el backend asigna el rol `owner`.
  En Numera esto equivale a propietaria y administradora principal, con más permisos que `admin`.

## Flujo nuevo

1. Crear cuenta desde `/register`.
2. El frontend llama a `POST /auth/register`.
3. Inicia sesión automáticamente mediante `POST /auth/login`.
4. Crea la empresa mediante `POST /companies/`.
5. El backend asigna al usuario como `owner`.
6. Entrada directa al dashboard.

## Tu usuario actual

Para el usuario ya creado:

```text
marta@numera.es
```

1. Entra desde `/login`.
2. Como todavía tiene `company_id = null`, Numera lo enviará a `/onboarding`.
3. Escribe el nombre de tu empresa.
4. Al crearla, tu usuario quedará como `owner`, es decir, administradora principal.

No hace falta volver a registrar ese correo.

## Instalación en Windows

Descomprime el ZIP en una carpeta nueva y ejecuta:

```cmd
copy .env.example .env.local
npm install
npm run dev
```

El archivo `.env.local` debe contener:

```env
NUMERA_BACKEND_URL=http://127.0.0.1:8000
```

## Arranque

Terminal del backend:

```cmd
uvicorn numera.main:app --reload
```

Terminal del frontend:

```cmd
npm run dev
```

Abre:

```text
http://localhost:3000
```
