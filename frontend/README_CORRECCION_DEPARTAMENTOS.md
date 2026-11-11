# Corrección del selector de departamentos

Se eliminó el filtro que ocultaba departamentos sin equipos. El selector ahora muestra todos los departamentos que devuelve `/api/departamentos/`.

Las solicitudes, equipos y departamentos se cargan de manera independiente: un error en una consulta no oculta las demás.

Para comprobarlo: ejecuta `npm run dev`, abre `http://127.0.0.1:5173/`, entra en Solicitudes de baja > Nueva solicitud. Debe aparecer Contabilidad, incluso si no tiene equipos. Para guardar una solicitud todavía debes registrar y seleccionar al menos un equipo asociado al departamento.

No se modifica el backend ni la base de datos.
