# DepoCom UHO — Integración de reportes (versión en revisión)

Este paquete se construyó sobre el archivo `backend(2).rar` recibido el 11/11/2026. Conserva las funciones existentes y agrega cuatro exportaciones.

## Endpoints nuevos

- `GET /api/reportes/equipos-deposito.xlsx`
- `GET /api/reportes/equipos-deposito.pdf`
- `GET /api/reportes/movimientos-piezas.xlsx`
- `GET /api/reportes/movimientos-piezas.pdf`

Las exportaciones de equipos respetan el filtrado de acceso por sede existente en `views_deposito.autorizado`. Los movimientos globales de piezas solo pueden exportarse con el rol administrador. Todas requieren sesión autenticada.

## Instalar

1. Haz copia de seguridad de `backend` y de la base de datos. Extrae este ZIP sobre tu carpeta `backend`, conservando `.env`.
2. En tu entorno virtual, ejecuta `python -m pip install -r requirements.txt`.
3. Ejecuta `python manage.py check` y `python manage.py makemigrations --check --dry-run`.
4. Ejecuta `python manage.py test core.test_reportes_formatos` y `python manage.py test core`.

Esta entrega no añade modelos ni migraciones.

## Estado real de validación

Se verificó sintaxis de los módulos Python. No se ejecutaron pruebas Django/PostgreSQL en el entorno de generación, por lo que la ejecución en el equipo del usuario es necesaria.

## Todavía pendientes

No se considera backend definitivo: faltan completar reportes adicionales (trazabilidad y solicitudes), avisos de los flujos heredados, documentación formal de API, revisión exhaustiva de auditoría y seguridad, e integración OAuth/OIDC institucional (requiere credenciales UHO).
