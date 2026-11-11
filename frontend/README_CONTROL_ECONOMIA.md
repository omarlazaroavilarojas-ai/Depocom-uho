# Integración de Control de Economía

Se conectó el componente existente `PanelEconomia.vue` a la opción `Control de economía` en `App.vue`. No se modificó el backend ni las rutas API.

## Instalación

Haz copia de seguridad de `frontend`, copia el contenido de este paquete sobre tu carpeta `frontend` y ejecuta `npm run dev`.

## Pruebas

1. Inicia sesión con un rol autorizado.
2. Abre Control de economía.
3. Comprueba la solicitud que haya superado revisión técnica.
4. Prueba las acciones permitidas según el estado, verificando que el estado cambie.

Nota: los endpoints `/api/solicitudes/{id}/remitir-economia/`, `iniciar-economia/`, `aprobar-economia/` deben existir en el backend. No se verificaron contra el servidor local.
