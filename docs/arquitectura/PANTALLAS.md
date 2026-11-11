# Análisis de las 11 pantallas

Fuente: [mockup.html](../referencias/mockup.html), HTML/CSS/JavaScript completo. IDs reales `sc0`–`sc10`; las rutas dibujadas son ejemplos, no despliegues confirmados. Se revisó el código estático; no se declara validación visual en navegador.

La única función JavaScript es `showScr(id, el)`: cambia la clase `on` de pestañas y paneles. Los inputs permiten edición nativa del navegador y existe un botón deshabilitado para pieza reservada. No hay llamadas HTTP, persistencia, router, validación de negocio ni autenticación. Ningún botón de gestión tiene manejador. Las acciones descritas a continuación son la intención visible pendiente de implementación.

## SC0 — Dashboard / Panel principal

- Finalidad: pendientes del técnico del depósito, indicadores y avisos.
- Campos/formularios/filtros: ninguno.
- Botones: Ver todas abre pendientes; Revisar abre revisión; Confirmar conduce a recepción. Campana sugiere notificaciones. Menú lateral dibujado sin navegación funcional.
- Tabla: número de solicitud, departamento, cantidad de equipos, estado, fecha, acción.
- Backend: usuario/rol/ámbito, solicitudes activas, equipos en depósito, piezas en almacén, despiezes pendientes, piezas instaladas, agenda y pendientes propios; permisos y notificaciones.
- Pendiente: calcular agregados, ordenar pendientes y enlazar acciones. Dashboard como agrupación visual del HTML; las métricas no son nuevos RF independientes.

## SC1 — Nueva solicitud de baja

- Finalidad: preparar y enviar baja (jefe de departamento), RF-02.
- Formulario: departamento, área y sede de solo lectura; centro de costo, fecha y justificación editables.
- Tabla: inventario, tipo, marca, modelo, serie, estado y eliminación.
- Botones: Cancelar; Guardar borrador; Importar desde Excel; Descargar plantilla; Agregar manual; papelera por fila; Enviar solicitud.
- Filtros/búsqueda: ninguno.
- Backend: adscripción del usuario, nomencladores, borrador y equipos, importación validada, archivo plantilla y transición de envío.
- Pendiente: selector de archivo (no existe input file), formulario manual, validación de duplicados/obligatorios, errores por fila, guardado/envío y bloqueo tras aprobación técnica. El formulario manual no está dibujado.

## SC2 — Aprobación de área

- Finalidad: decidir sobre solicitudes de departamentos supervisados, RF-03.
- Campos de solo lectura: departamento, centro de costo, solicitante, fecha, justificación. Comentario editable.
- Tabla: inventario, tipo, marca/modelo, estado. Tarjetas: cantidades por tipo y total.
- Botones superiores Aprobar/Rechazar y duplicados inferiores Aprobar solicitud/Rechazar solicitud: misma decisión prevista.
- Filtros/búsqueda: ninguno en el detalle.
- Backend: detalle completo, resumen real, ámbito del jefe de área, estado vigente, historial y registro de decisión/notificación.
- Pendiente: validar comentario obligatorio al rechazar, permisos, actualización de estado. El resumen muestra siete equipos y la tabla tres; no usar cifras como regla.

## SC3 — Revisión técnica

- Finalidad: agenda y checklist físico, RF-04.
- Formulario: fecha, hora, técnico de solo lectura. Por equipo: checkbox, selector Sí procede/No procede y comentario opcional; estado reportado informativo.
- Botones: Agendar, Guardar revisión, Enviar a jefe soporte.
- Tabla/filtros: lista checklist; no hay búsqueda/filtro. Agenda solo figura en menú lateral.
- Backend: equipos aprobados por área, agenda, técnico asignado, resultados individuales y envío para aprobación técnica.
- Pendiente: persistir agenda/checklist; resolver duplicación checkbox/selector; vista y acción de aprobación final del jefe de soporte no existen aquí.

## SC4 — Economía / Movimiento contable

- Finalidad: validar procesamiento externo y aprobar traslado contable al depósito, RF-05.
- Campos de solo lectura: departamento origen, centro de costo, destino y sede.
- Tabla: inventario, tipo, descripción, marca/modelo, serie; únicamente listado técnicamente aprobado.
- Botones: Aprobar movimiento y Confirmar movimiento contable y aprobar traslado (misma intención).
- Filtros/búsqueda: ninguno; pendientes/historial solo en menú.
- Backend: solicitud autorizada para sede, listado definitivo, estado económico y aprobador.
- Pendiente: aprobación/notificación y bandeja económica. El aviso exige procesar en sistema contable; no implementa integración automática. Tampoco existe la acción del jefe de departamento para solicitar movimiento.

## SC5 — Inventario del depósito

- Finalidad: consultar equipos recibidos y acceder a detalle/despiece, RF-06/RF-11.
- Campos/filtros: área, departamento, tipo recurso, estado (Todos/Disponible/En Despiece/Trasladado), búsqueda «Inv, marca, serie…».
- Botones: Excel, PDF, Filtrar; lupa por fila (detalle/trazabilidad sugerido); herramienta por fila disponible (despiece sugerido, sin etiqueta textual que precise acción).
- Tabla: inventario, tipo, marca/modelo, origen, entregante, receptor, fecha, estado, acciones. Total de equipos.
- Backend: catálogo de filtros, inventario y total autorizado, responsables, origen, permisos y exportaciones del conjunto filtrado (propuesta de coherencia).
- Pendiente: filtros reales, detalle y descargas. RF-06 requiere también fecha/modelo; el HTML no presenta todos explícitamente. No existe checklist de recepción ni formulario entregante/receptor.

## SC6 — Solicitud y ejecución de despiece

- Finalidad: solicitar y registrar piezas tras aprobación, RF-07.
- Solicitud: técnico de solo lectura, fecha y hora sugeridas, participantes adicionales, justificación (campo HTML adicional); búsqueda por inventario y lista de equipos con origen/ingreso/estado.
- Ejecución: selector equipo, selector tipo de pieza; ejemplo fijo «RAM DDR3» con marca, capacidad, velocidad, serie, estado Bueno/Regular/Malo y descripción.
- Botones: Enviar a jefe soporte, Agregar equipo, quitar equipo (×), Añadir pieza, Registrar pieza en almacén.
- Tablas/filtros: lista de equipos; búsqueda por inventario; sin tabla final de piezas registradas.
- Backend: equipos elegibles y sus datos, solicitud, participantes, agenda aprobada, esquema configurable por tipo, piezas creadas y origen.
- Pendiente: búsqueda automática, carga dinámica de campos (incluido modelo requerido por PDF según tipo), aprobación con fecha/hora, impedir ejecutar sin aprobación, registrar piezas y finalizar despiece. La sección de ejecución ya es visible, sin bloqueo real. Velocidad es ejemplo de campo adicional, no obligación para todo tipo.

## SC7 — Almacén de piezas

- Finalidad: disponibilidad, búsqueda, extracción e historial, RF-08.
- Filtros: tipo, marca, capacidad y estado (Todos/Bueno/Regular).
- Presentación: tarjetas con tipo/marca, disponibilidad, atributos (capacidad/velocidad/RPM/potencia/conector/serie/estado), equipo/departamento origen, fecha, stock. Resumen RAM, HDD/SSD, fuentes y otras.
- Botones: Solicitar extracción, Exportar, Buscar, Extraer por tarjeta, Historial; Reservada deshabilitado en ejemplo.
- Backend: filtros y campos configurables, unidades y agregados disponibles, reservas e historial, exportaciones PDF/Excel según RF-11.
- Pendiente: búsqueda/stock real, filtros modelo/serie/disponibilidad de RF-08.1, agrupación coherente entre tarjeta y serie individual. No asumir que una pieza con serie representa tres unidades.

## SC8 — Solicitud de extracción de pieza

- Finalidad: solicitar pieza y registrar destino, RF-09.
- Campos: tipo; marca, capacidad y modelo rotulados opcionales; tipo de destino (otro departamento/propio depósito); inventario receptor actualizable al instalar; departamento destino; justificación (añadida en HTML).
- Botón: Enviar a jefe soporte.
- Tabla/filtros: criterios del formulario; línea temporal de creación, pendiente de aprobación, extracción e instalación; no hay tabla de coincidencias ni botón de instalación.
- Backend: tipos/criterios, coincidencias disponibles, destino, solicitud, aprobación, reserva y eventos de instalación.
- Pendiente: mostrar coincidencias, aprobar/reservar sin doble asignación, registrar instalación y actualizar historial. Aclarar si modelo/capacidad son siempre opcionales: RF-09 los enumera sin esa precisión.

## SC9 — Trazabilidad de equipos y piezas

- Finalidad: reconstruir historial por inventario, RF-11.
- Búsqueda: número de inventario, botón Buscar.
- Solo lectura: tipo, marca/modelo, serie y estado actual.
- Línea temporal: solicitud, aprobación área, revisión/aprobación soporte, Economía, recepción, despiece y situación actual.
- Tabla de piezas: tipo, marca/modelo, capacidad, serie, estado e inventario/departamento de instalación.
- Botón Exportar: formato no seleccionable en maqueta; PDF y Excel exigidos por RF-11.
- Backend: equipo, eventos ordenados con responsables/fechas, piezas origen y destino, movimientos e instalaciones.
- Pendiente: consulta y exportación reales, búsqueda/historial individual de pieza y equipos receptores externos al depósito, controles de acceso. Ejemplos varían respecto a SC5/SC7.

## SC10 — Administración / Nomencladores de áreas

- Finalidad: administración de catálogos; solo está dibujado CRUD de área, RF-01.
- Búsqueda: Buscar área.
- Tabla: nombre, sede, jefe, cantidad de departamentos y acciones.
- Modal permanentemente visible: nombre del área, sede, jefe de área, descripción.
- Botones: Nueva área, Editar, papelera, Cancelar, Guardar.
- Menú sin implementación: áreas, departamentos, tipos de recursos, tipos de piezas, usuarios y roles, sedes, logs.
- Backend: listado/total de áreas, sedes, usuarios elegibles, departamentos agregados, permisos; CRUD y validaciones.
- Pendiente: búsqueda, apertura/cierre del modal, CRUD real y política de borrado con referencias; formularios restantes, campos dinámicos, permisos y logs restringidos al administrador. No hay pantalla propia del consultor.

## Diseño y cobertura pendiente

Conservar como referencia la barra lateral azul, encabezados, tarjetas, tablas, formularios, estados por color, timeline, modal y variables CSS (`#003366`, `#0055a5`, etc.). El Manual de Identidad UHO sigue pendiente; el HTML no acredita conformidad. Los tamaños de letra pequeños, menú de ancho fijo, botones de iconos sin nombre accesible y ausencia de media queries requieren validación responsive y accesible futura. Hay grids adaptativos y desbordamiento, pero eso no prueba RNF-01.

Vistas o flujos necesarios por PDF que aún no están dibujados: recepción física; solicitud de movimiento por departamento; aprobación técnica final; aprobación/agenda de despiece; aprobación de extracción e instalación final; solicitud/aprobación de traslado; reportes completos; notificaciones internas; CRUD restantes y consulta de logs. Su diseño será trabajo de otra fase autorizada, no nuevas pantallas inventadas como requisitos independientes.
