# Reglas de trabajo de DepoCom UHO

Estas instrucciones se aplican a todo el proyecto. Respetar instrucciones explícitas del usuario y trabajar por fases con autorización antes de pasar a la siguiente.

## Fuentes y alcance

- Leer y respetar `docs/referencias/referencia.pdf`: es el PDF disponible, descrito inicialmente por el usuario como `requisitos.pdf`. Si cambia la fuente o aparece otro PDF, registrar la diferencia antes de sustituir requisitos.
- Respetar el diseño de `docs/referencias/mockup.html` y sus once pantallas. El HTML es referencia visual y no sustituye reglas del PDF. Completar funciones exigidas por el PDF aunque no estén dibujadas, dentro de fase autorizada.
- No eliminar, modificar ni sobrescribir documentos originales. Si no puede extraerse un PDF requerido, informar y detener su análisis; no inventar contenido.
- No inventar requisitos ni credenciales/configuraciones institucionales. Marcar propuestas adicionales y dudas explícitamente y mantener trazabilidad hacia fuente/página/RF/RNF.
- Consultar `docs/arquitectura/` y `TODO.md` antes de implementar. Documentar contradicciones, no resolverlas mediante reglas de negocio ocultas.

## Fases y estructura

- La tarea inicial autoriza solo análisis/documentación. No crear backend Django, frontend Vue, instalar dependencias ni configurar Docker durante esa tarea.
- No avanzar a otra fase sin autorización expresa del usuario. Un TODO o diseño propuesto no constituye autorización. Detenerse al completar la fase solicitada.
- Conservar estructura `backend/`, `frontend/`, `docs/` y archivos raíz. Respetar cambios existentes del usuario; no hacer limpiezas ni reestructuraciones ajenas al alcance.
- Stack solicitado: Python/Django/DRF, Vue 3/Vite, PostgreSQL, Docker Compose, Nginx, OpenAPI/Swagger y Git/GitHub. Adaptar el ejemplo Laravel del PDF, sin copiar dependencias PHP.

## Seguridad y calidad

- Aplicar permisos en servidor por rol, ámbito y objeto, además de guiar acciones en interfaz por estado. No confiar en ocultar botones ni permitir saltos de aprobación mediante edición genérica de estado.
- Validar entradas en frontend/backend y proteger contra OWASP Top 10, inyección, XSS, CSRF e IDOR. Usar transacciones/restricciones para inventario y reservas concurrentes.
- Preservar trazabilidad de equipos/piezas y auditoría de acciones con actor/fecha/IP. Logs accesibles únicamente al administrador; no registrar secretos/tokens ni datos personales innecesarios.
- Prever OAuth2/OIDC institucional sin almacenar contraseñas locales. No inventar endpoints, client IDs, secretos, scopes ni claims de la UHO.
- HTTPS/TLS, cifrado de datos personales en reposo, minimización y secretos fuera del repositorio. Seleccionar y comprobar mecanismos al implementar, sin declarar seguridad solo por usar un framework.
- Nomencladores y tipos administrables; no fijar en código los ejemplos del prototipo como catálogos definitivos o datos reales.

## Verificación obligatoria

- Probar el código antes de declarar que funciona. Ejecutar comprobaciones apropiadas al cambio: servicios/API, permisos/ámbitos/estados, integridad y concurrencia cuando aplique; interfaz y flujos completos para cambios de usuario.
- Registrar qué se probó y el resultado. Si no puede ejecutarse una prueba, explicar la limitación y no declarar verificado ese comportamiento.
- Contrastar interfaz con HTML y Manual de Identidad UHO disponible; comprobar responsive, validación y mensajes en español.
- Mantener requisitos, pantallas, modelo, arquitectura, matriz y TODO coherentes con decisiones aprobadas. Marcar tareas completas solo con su criterio satisfecho.
- En cambios exclusivamente documentales comprobar cobertura, enlaces y preservación de fuentes; no instalar dependencias ni crear pruebas de aplicación para simular avances de otra fase.
