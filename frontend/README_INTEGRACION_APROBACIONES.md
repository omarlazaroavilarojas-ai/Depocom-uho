# Integración del flujo de aprobaciones

Se ha conectado el componente `PanelAprobaciones.vue`, que ya existía en el frontend, con la opción **Aprobación de área** del menú de `App.vue`. Antes, esa opción solo mostraba una tabla de consulta.

En el panel, los botones disponibles dependen de `sesion.roles` y del estado de cada solicitud. El backend debe validar todos los permisos y transiciones. El panel permite presentar borradores, registrar la decisión del área y muestra también las acciones de revisión técnica ya implementadas en el componente.

## Instalación

1. Haz una copia de seguridad de tu frontend.
2. Sustituye la carpeta frontend por el contenido de este paquete o copia solo `src/App.vue` si el resto de tu proyecto no ha cambiado.
3. Desde frontend ejecuta `npm install` si no tienes dependencias y `npm run dev`.
4. Mantén Django activo en el puerto 8000.
5. Entra con un usuario que tenga el rol correspondiente, abre **Aprobación de área** y prueba con una solicitud de prueba.

**Nota:** No se modificó Django. Si los botones no aparecen, verifica la estructura de `/api/sesion/` (en especial `roles`) y los permisos asignados al usuario. No se ha verificado la compilación ni el funcionamiento contra tu backend local en este entorno.
