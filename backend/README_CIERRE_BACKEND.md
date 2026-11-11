# DepoCom UHO — Cierre de notificaciones y documentación

## Instalación
1. Conservar `.env` y respaldar la base de datos antes de reemplazar el backend.
2. `python -m pip install -r requirements.txt`
3. `python manage.py check`
4. `python manage.py makemigrations --check --dry-run`
5. `python manage.py test core.test_documentacion_notificaciones`
6. `python manage.py test core`

## Documentación de API
- `/api/schema/`: esquema OpenAPI (requiere iniciar sesión).
- `/api/docs/`: Swagger UI (requiere iniciar sesión).

Los endpoints ya existentes de `/api/` conservan sus permisos. La generación automática de esquema de vistas APIView puede requerir decoradores `extend_schema` para mostrar con precisión cuerpos de solicitud y respuesta.

## Notificaciones
Se añaden avisos al solicitante cuando se registra un evento del historial de solicitud y avisos a roles correspondientes cuando se presenta o progresa el trámite. Se notifican también las solicitudes y decisiones de traslado. Los avisos existentes del circuito de piezas se conservan.

## Limitaciones para entrega institucional
- OAuth2/OIDC con `auth.uho.edu.cu` exige credenciales, metadatos y pruebas con el proveedor institucional.
- Auditoría global de acciones e IP y cobertura completa de permisos deben verificarse antes de producción.
- Ejecutar pruebas en PostgreSQL y validación de despliegue HTTPS con el servidor real.
- Este paquete no demuestra los objetivos de rendimiento o disponibilidad del documento técnico.
