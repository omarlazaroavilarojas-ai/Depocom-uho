# DepoCom UHO — Frontend Vue, etapa 2

Este paquete amplía la interfaz Vue 3 con **creación y consulta de solicitudes de baja** conectadas a la API Django real.

## Instalación

1. Haz copia de seguridad de tu carpeta `frontend` actual.
2. Copia los archivos de este paquete a `C:\Users\Darksiders\Desktop\DepoCom-UHO\frontend` (conserva tu `.env`, si existe).
3. Conserva la carpeta `node_modules` que ya tienes instalada. Si no existe, ejecuta `npm install`.
4. Arranca Django en `127.0.0.1:8000` y luego ejecuta `npm run dev` en `frontend`.
5. Abre **http://127.0.0.1:5173/** (evita `localhost` por las cookies de sesión).

## Solicitudes de baja

- Consulta las solicitudes visibles para el usuario autenticado.
- «Nueva solicitud» carga equipos y departamentos desde `/api/equipos/` y `/api/departamentos/`.
- Permite seleccionar varios equipos del mismo departamento, ingresar número y observaciones.
- Envía `POST /api/solicitudes/` con `numero`, `observaciones`, `equipos` (IDs) y CSRF.
- Los permisos los comprueba el backend: jefe de departamento (de su departamento) o administrador.
- Los equipos deben estar registrados previamente y asociados a un departamento.

**Aún pendiente:** importar Excel, editar solicitudes, presentar para aprobación y demás flujos operativos en la nueva interfaz. No se cambió el backend ni se inventó un endpoint de importación.

## Verificación

`npm run build` para comprobar la compilación. No hace falta ejecutar migraciones Django.
