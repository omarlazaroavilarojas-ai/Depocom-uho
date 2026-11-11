# DepoCom UHO — Corrección de cobertura Swagger

Este paquete parte del backend(3).rar enviado por el usuario, después de 103 pruebas exitosas en su equipo.

## Cambios

- Se documentaron explícitamente 38 métodos de APIView mediante `@extend_schema`.
- Se asignaron `operation_id` únicos para evitar la colisión de las rutas de depósito.
- Se añadió `core/test_swagger_cobertura.py` para comprobar que el esquema contiene las rutas principales y no repite operationIds.
- No se modificaron modelos, migraciones ni reglas de negocio.

**Límite:** las vistas que construyen respuestas manualmente se describen con esquemas genéricos (`OpenApiTypes.ANY`) y los cuerpos de entrada con `OpenApiTypes.OBJECT`. Esto evita la exclusión de rutas, pero **no equivale a documentación detallada de todos los campos**. Para obtener contratos precisos habrá que introducir serializadores de entrada/salida y ejemplos por operación.

## Comprobación

Desde `backend`:

```powershell
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py test core.test_swagger_cobertura
.venv\Scripts\python.exe manage.py test core
.venv\Scripts\python.exe manage.py spectacular --file schema.yml --validate
```

Abrir `http://127.0.0.1:8000/api/docs/` después de iniciar sesión.

No se han ejecutado pruebas Django ni PostgreSQL en el entorno de preparación del ZIP. Se ha comprobado la sintaxis Python.
