# DepoCom UHO — Bloque de consulta de solicitudes

Se amplió `src/components/SolicitudesBaja.vue` con búsqueda, filtro por estados reales de la API y vista expandible de detalles. Se conserva el formulario de creación y la configuración del proxy/CSRF que estaba en el archivo entregado.

## Instalación
1. Haz una copia de seguridad de tu carpeta `frontend` actual.
2. Sustituye el contenido de la carpeta `frontend` por el contenido de este ZIP (no borres tu backend).
3. En `frontend`, ejecuta `npm install` (si no tienes dependencias) y `npm run dev`.
4. Entra a `http://127.0.0.1:5173/`, inicia sesión y abre «Solicitudes de baja».

## Pruebas manuales
- Comprueba que el listado carga y que «Ver detalles» muestra los datos existentes.
- Busca por número y filtra por estado.
- Crea una solicitud nueva y verifica que sigue apareciendo en la lista.

## Alcance
La vista de detalles usa los campos incluidos en `GET /api/solicitudes/`. No se inventan endpoints de aprobación, ni se cambian permisos del backend. Si la API no incluye detalles de equipos, se indica en pantalla. No se pudo ejecutar `npm run build` en el entorno de preparación porque no se pudieron instalar dependencias de npm; comprueba el build localmente.
