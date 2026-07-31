NUMERA INTEGRADO - FRONTEND + BACKEND
=====================================

PRIMERA VEZ
1. Descomprime el ZIP completo.
2. Haz doble clic en INSTALAR_NUMERA.bat.
3. Al terminar, haz doble clic en INICIAR_NUMERA.bat.

SIGUIENTES VECES
- Solo haz doble clic en INICIAR_NUMERA.bat.
- El script arranca automáticamente el backend, el frontend y abre el navegador.

URLS
- Aplicación: http://localhost:3000
- Backend/API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

CORRECCIÓN INCLUIDA
- Una empresa creada queda activada automáticamente.
- Las cuentas antiguas con membresía pero sin empresa seleccionada se reparan al iniciar sesión.
- El frontend comprueba /companies/my y activa una empresa disponible antes de entrar.
- El onboarding hace una activación explícita tras crear la empresa.

IMPORTANTE
El frontend es la interfaz y el backend es el servidor que procesa login, base de datos,
OCR y facturas. Ambos deben estar ejecutándose. INICIAR_NUMERA.bat lo hace por ti.
