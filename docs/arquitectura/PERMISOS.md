# Permisos de los siete roles

Fuente: [referencia.pdf](../referencias/referencia.pdf), secciones 2.1–2.2 (pp. 5–6), RF-01–12 y RNF-02.3/RNF-06.3. Complementa [REQUISITOS.md](REQUISITOS.md), sin sustituir ni ampliar permisos por intuición. Matriz documental; no hay autorización implementada.

## Roles y ámbitos

| Código | Rol | Restricción respaldada y pregunta pendiente |
|---|---|---|
| ADM | Administrador del sistema | Acceso total según sección 2.1 y matriz. No omite validaciones, secuencia de aprobación ni integridad (propuesta técnica); solo él consulta auditoría |
| JD | Jefe de departamento | Solicitudes de su departamento, seguimiento y reportes propios. No modificar listado tras aprobación técnica |
| JA | Jefe de área | Solicitudes de departamentos bajo su supervisión; reportes propios del área. Rechazo exige comentario |
| TS | Técnico de soporte | Uno por departamento/área y uno global del depósito. RF-06/07 asignan recepción y despiece al técnico del depósito. RF-04.1 dice todas las solicitudes aprobadas por área; falta conciliar ese «todas» con asignación territorial. No extender escritura a otra área/sede por silencio |
| JST | Jefe de soporte técnico | Único a nivel universidad; aprobación técnica, despiece, extracción y traslado. Matriz también permite agendar, confirmar entrega y registrar piezas; confirmar alcance frente a descripciones operativas |
| ECO | Jefe de Economía | Uno por sede; tramita movimientos de esa sede. Matriz autoriza reportes, pero no precisa si su lectura se limita a sede: pendiente |
| CON | Consultor | Lectura de reportes, inventarios y estados, sin modificación. No aparece en matriz 2.2, sí en descripción 2.1; ámbito territorial de lectura pendiente. Sin logs por RNF-06.3 |

## Matriz de lectura y modificación

L = lectura; M = modificación mediante acción concreta (no CRUD indiscriminado); C/R/U/D = crear/leer/actualizar/eliminar. G = global explícito; D = departamento propio; A = área supervisada; S = sede propia; DEP = técnico del depósito; ? = ámbito o permiso no definido. N = prohibición explícita en matriz/descripción; ND = no definido por PDF, **no concedido** hasta aclaración. L? o M? reconoce la acción documentada pero deja pendiente su alcance; no equivale a acceso global. CRUD* conserva la necesidad de política de borrado de referencias históricas.

| Acción | ADM | JD | JA | TS | JST | ECO | CON | Fuente / condición |
|---|---|---|---|---|---|---|---|---|
| CRUD sedes/áreas/departamentos | CRUD* G | N | N | N | N | N | N | RF-01.1–3, matriz CRUD |
| CRUD tipos recursos/piezas y campos | CRUD* G | N | N | N | N | N | N | RF-01.4–5 |
| CRUD usuarios/roles/permisos | CRUD* G | N | N | N | N | N | N | RF-01.6–7; identidad institucional no implica contraseñas locales |
| Crear baja | C G | C D | N | N | N | N | N | RF-02.1, matriz |
| Importar Excel / agregar equipos manualmente | M G | M D | N | N | N | N | N | RF-02.2–3, descripción JD |
| Descargar plantilla | L G | L D | ND | ND | ND | ND | ND | RF-02.5 en flujo JD; otros accesos no asignados |
| Guardar/editar borrador y enviar | M G | M D | ND | ND | ND | ND | N | RF-02 y fase 1; instante de bloqueo previo a aprobación técnica por acordar |
| Editar listado después de aprobación técnica | ND | N | ND | ND | ND | ND | N | RF-02.7 solo prohíbe JD; acceso total ADM no autoriza inventar flujo de corrección |
| Leer solicitud/listado/resumen para gestionar | L G | L D | L A | L? | L G | L S económico | L? estados | RF-03/04/05, roles; consultor no recibe detalle sensible por defecto |
| Aprobar/rechazar baja por área | M G | N | M A | N | N | N | N | RF-03.3; comentario obligatorio al rechazar |
| Agendar revisión técnica | M G | N | N | M? | M G | N | N | Matriz 2.2; RF-04 asigna operación a TS |
| Guardar checklist técnico | M G | ND | ND | M? | ND | ND | N | RF-04.3, fase 3–4; no inferir que agendar otorga editar checklist |
| Enviar revisión al JST | M G | ND | ND | M? | ND | ND | N | HTML SC3 y flujo RF-04; acción de envío técnico propuesta, no nueva aprobación |
| Aprobar listado técnico final | M G | N | N | N | M G | N | N | RF-04.4 y matriz |
| Solicitar movimiento económico | M G | M D | N | N | N | N | N | RF-05.1 y matriz; listado definitivo inalterado |
| Registrar inicio/procesamiento económico interno | M? | ND | ND | ND | ND | M? S | N | PDF describe proceso externo, no disparador interno; no habilitar transición aún |
| Aprobar movimiento contable | M G | N | N | N | N | M S | N | RF-05.3; sede competente |
| Confirmar recepción/checklist y responsables | M G | N | N | M DEP | M G | N | N | RF-06 y matriz; cierre parcial pendiente D-03 |
| Consultar inventario depósito | L G | L D vía reportes | L A vía reportes | L? | L G | L? | L? | RF-06/11; alcance de lectura TS/ECO/CON pendiente |
| Solicitar despiece | M G | N | N | M DEP | N | N | N | RF-07.1 y matriz; técnico del depósito |
| Aprobar despiece y confirmar agenda | M G | N | N | N | M G | N | N | RF-07.3 |
| Ejecutar despiece y cerrar equipo | M G | ND | ND | M DEP | ND | ND | N | RF-07.4; registrar piezas no implica permiso de ejecución para JST |
| Registrar piezas en almacén | M G | N | N | M DEP | M G | N | N | RF-07 y matriz; solo despiece aprobado |
| Consultar piezas/stock/historial | L G | L D vía reportes | L A vía reportes | L? | L G | L? | L? | RF-08/11 y matriz de reportes |
| Solicitar extracción de pieza | M G | N | N | M? | N | N | N | RF-09.1, matriz; destino de cualquier departamento no amplía ámbito del técnico |
| Aprobar extracción y reservar unidad | M G | N | N | N | M G | N | N | RF-09.3–4, reserva automática ligada a aprobación |
| Registrar salida física separada | M? | ND | ND | M? | ND | ND | N | Paso ilustrado SC8; obligatoriedad/actor operativo por confirmar |
| Registrar instalación/receptor exacto | M G | ND | ND | M? | ND | ND | N | RF-09.5, fase 8; debe existir reserva aprobada |
| Cancelar/caducar/devolver/reasignar reserva | ND | ND | ND | ND | ND | ND | N | No definido; no hay permisos ni automatismos inventados |
| Crear solicitud de traslado | M G | ND | ND | ND | ND | ND | N | RF-10 no asigna solicitante; ADM por acceso total, flujo concreto pendiente D-06 |
| Aprobar traslado | M G | ND | ND | ND | M G | ND | N | RF-10.2; para otros roles ND, no autorización |
| Marcar Trasladado y registrar movimiento | M G | ND | ND | ND | M G ligado a aprobación | ND | N | RF-10.3; no concede ejecución física independiente; momento exacto pendiente |
| Leer reportes/trazabilidad | L G | L D | L A | L? | L G | L? | L? | RF-11, matriz 2.2 y descripción CON |
| Exportar reportes PDF/Excel | L G | L D | L A | L? | L G | L? | L? | RF-11.6; mismos filtros/ámbito que lectura, sin permiso de escritura adicional |
| Recibir/leer notificaciones destinadas al usuario | L propias | L propias | L propias | L propias | L propias | L propias | ND | RF-12; recibir no concede acceso a solicitud fuera de ámbito; ADM/CON no son destinatarios nuevos por su rol |
| Marcar aviso como leído | M propias | M propias | M propias | M propias | M propias | M propias | ND | Propuesta técnica para notificación recibida, no modificación de negocio |
| Consultar logs de auditoría | L G | N | N | N | N | N | N | RNF-06.3 |
| Editar/borrar logs o historia ya emitida | ND | ND | ND | ND | ND | ND | N | Propuesta: impedir edición directa; corrección/retención necesitan política, no CRUD libre |

Las celdas N se apoyan en NO explícitos o en la lectura exclusiva del consultor; ND conserva silencios de la fuente. Para auditar la distinción, prevalecen siempre sección/RF citados y el ámbito descrito. No existe un rol «técnico del depósito» adicional: DEP es ámbito de TS. Destinatarios concretos de notificaciones siguen RF-12, no todas las celdas L propias producen mensajes nuevos.

## Aplicación y pruebas propuestas

- Autorizar por acción + rol + ámbito + estado + objeto; filtrar listados, búsquedas, conteos, exportaciones y enlaces de trazabilidad con la misma política. Denegar por defecto ND y ámbitos sin resolver, sin reinterpretar L? como prohibición definitiva del requisito.
- Sede de Economía se compara con la sede histórica de la baja/movimiento. JA debe supervisar el departamento de origen; JD debe pertenecer al departamento de su solicitud. Confirmar política si cambian jefes/adscripciones durante un trámite.
- Cambiar el inventario destino o una FK en una petición no debe ampliar permisos; acceso a pieza no concede todo el historial personal de otros ámbitos. Definir vistas parciales de trazabilidad cuando crucen departamentos/sedes.
- Probar cada celda autorizada y cada denegación: usuario de otra sede/área/departamento, estados inválidos, cambios de rol y accesos directos por ID. La interfaz muestra acciones válidas, pero la API es quien las impone.
- Lecturas sin permiso no filtran existencia de otros objetos; logs siempre exclusivos del administrador. Escrituras del sistema (reservar, notificar, auditar) son efectos de comandos autorizados, no roles humanos nuevos.

## Confirmaciones pendientes

1. D-04: ¿qué solicitudes puede leer/revisar cada técnico y qué ámbito tienen los reportes de TS/ECO/CON? ¿JST confirma recepción/registra piezas tal como indica matriz, además del técnico descrito en RF-06/07?
2. D-02: ¿quién puede editar un borrador enviado, corregir una aprobación o iniciar En Proceso Económico? ¿Cómo se tramita un rechazo/reenvío?
3. D-03/D-05/D-06: ¿quién cierra recepción parcial, gestiona excepciones de reservas y solicita/ejecuta traslado físico? No asignar esas acciones por conveniencia.
4. ¿Se admiten varios roles simultáneos y cómo se combinan ámbitos/conflictos de aprobación? La relación N:M representa capacidad técnica, no autoriza acumulación ni autoaprobación institucional.
5. ¿Cómo se mantiene acceso histórico al cambiar jefaturas y cómo se muestran cadenas de trazabilidad entre áreas? Confirmar antes de fijar políticas definitivas.

Estas preguntas complementan D-02–D-06/D-13 de [REQUISITOS.md](REQUISITOS.md); se resolverán con el usuario/institución en una fase autorizada.
