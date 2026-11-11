# Rediseño visual DepoCom UHO

- Paleta propuesta a partir de los valores del manual institucional discutidos: azul #212D57 y verde #93BA22.
- Conserva los componentes y rutas existentes.
- Añade modo claro/oscuro (se restablece a claro al recargar).
- Añade un gráfico de solicitudes con conteos consultados en /api/solicitudes/.
- Animaciones suaves con respeto a `prefers-reduced-motion`.

## Instalación
Copia los archivos del ZIP sobre tu carpeta `frontend` tras hacer una copia de seguridad. En la carpeta frontend ejecuta `npm install` si no tienes dependencias, luego `npm run dev`. El backend no necesita cambios.

## Comprobaciones
1. Inicia sesión.
2. Revisa Panel general y verifica las cifras.
3. Cambia el tema con el botón de luna/sol en la barra superior.
4. Recorre Solicitudes, Recepción, Despiece, Inventario y Administración y prueba sus formularios.

Los gráficos reflejan los registros que devuelve la API; si esta pagina resultados, los conteos solo incluyen la página recibida. No son cifras globales verificadas en ese caso.
