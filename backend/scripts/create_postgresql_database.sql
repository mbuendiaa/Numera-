-- Ejecutar conectado como usuario administrador de PostgreSQL.
-- Cambia la contraseña antes de usarlo fuera de tu ordenador.
CREATE USER numera WITH PASSWORD 'numera';
CREATE DATABASE numera OWNER numera ENCODING 'UTF8';
GRANT ALL PRIVILEGES ON DATABASE numera TO numera;
