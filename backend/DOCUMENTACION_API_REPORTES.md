# DepoCom UHO — Reportes de trazabilidad (entrega de revisión)

Todas las rutas requieren sesión autenticada. Los tres reportes nuevos están **limitados a Administrador del Sistema** hasta implementar reglas de visibilidad por sede y departamento.

| Ruta | Formatos | Contenido |
|---|---|---|
| `/api/reportes/solicitudes.xlsx` | xlsx, pdf | Solicitudes, estado, departamento, solicitante y fecha |
| `/api/reportes/historial-solicitudes.xlsx` | xlsx, pdf | Historial de acciones, usuario, fecha y descripción |
| `/api/reportes/trazabilidad-piezas.xlsx` | xlsx, pdf | Origen, destino y fechas de piezas recuperadas |

Cambiar `.xlsx` por `.pdf` para obtener el PDF. Las exportaciones previas `equipos-deposito` y `movimientos-piezas` se mantienen.

## Validación

```powershell
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py test core.test_reportes_trazabilidad
.venv\Scripts\python.exe manage.py test core
```

No se modifican modelos ni se necesitan migraciones nuevas. Conservar `.env` existente. **Pendientes:** auditoría de seguridad integral, OpenAPI/Swagger, cobertura completa de notificaciones y conexión SSO institucional.
