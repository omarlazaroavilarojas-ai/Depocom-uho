# Requisitos de DepoCom UHO

Análisis documental, 10 de noviembre de 2026. Fuente normativa disponible: [referencia.pdf](../referencias/referencia.pdf), versión 1.0 (2025), 16 páginas, leído íntegramente mediante extracción de texto. El archivo solicitado como `requisitos.pdf` no existe con ese nombre. No se renombra el original. Referencia visual: [mockup.html](../referencias/mockup.html), leído completo. Las páginas citadas corresponden al PDF, contando portada.

El PDF determina el comportamiento; el HTML determina la referencia visual. Las decisiones técnicas de los documentos asociados son propuestas, no requisitos adicionales aprobados. No hay aplicación implementada por esta tarea.

## Requisitos funcionales

### RF-01 — Gestión de nomencladores (p. 6)

- RF-01.1: CRUD de sedes: nombre y dirección.
- RF-01.2: CRUD de áreas: nombre, descripción, sede y jefe de área.
- RF-01.3: CRUD de departamentos: nombre, tipo Departamento/Dirección/Grupo, área, centro de costo y jefe.
- RF-01.4: CRUD de tipos de recursos: computadora, monitor, teclado, impresora, TV, UPS, etc.; son ejemplos administrables.
- RF-01.5: CRUD de tipos de piezas con campos configurables: marca, modelo, capacidad, estado, serie, descripción y adicionales.
- RF-01.6: CRUD de roles y permisos.
- RF-01.7: CRUD de usuarios integrado con `auth.uho.edu.cu`.

### RF-02 — Solicitud de baja (pp. 6–7)

- RF-02.1: el jefe de departamento crea la solicitud con departamento, área, sede, centro de costo, fecha y justificación.
- RF-02.2: importar Excel con número de inventario, tipo de recurso, modelo, marca, número de serie y estado Roto/Funcionando.
- RF-02.3: agregar equipos manualmente.
- RF-02.4: impedir inventarios duplicados dentro de la solicitud.
- RF-02.5: descargar plantilla Excel.
- RF-02.6: estados enumerados: Borrador, Enviada, Aprobada por Área, Rechazada, En Revisión Técnica, Aprobada Técnicamente, Pendiente Movimiento Economía, En Proceso Económico, Aprobada por Economía y Recibida en Depósito.
- RF-02.7: el jefe de departamento no puede modificar el listado después de la aprobación técnica.

### RF-03 — Aprobación de área (p. 7)

- RF-03.1: notificar al jefe de área al enviarse una solicitud de su departamento.
- RF-03.2: mostrar listado completo y cantidades agrupadas por tipo de recurso.
- RF-03.3: aprobar o rechazar; comentario obligatorio en el rechazo.
- RF-03.4: notificar el resultado al jefe de departamento.

### RF-04 — Revisión técnica (p. 7)

- RF-04.1: el técnico consulta solicitudes aprobadas por área pendientes de revisión.
- RF-04.2: agenda fecha y hora de revisión física.
- RF-04.3: checklist individual: procede/no procede a baja y comentario.
- RF-04.4: el jefe de soporte técnico aprueba el listado final.
- RF-04.5: notificar resultado y listado definitivo al jefe de departamento y al jefe de área.

### RF-05 — Movimiento a Economía (p. 7)

- RF-05.1: el jefe de departamento solicita movimiento sin alterar el listado aprobado.
- RF-05.2: Economía de la sede consulta departamento, centro de costo y listado con inventario, tipo, descripción y serie.
- RF-05.3: Economía aprueba el movimiento contable y se notifica automáticamente a soporte técnico.

### RF-06 — Recepción en depósito (pp. 7–8)

- RF-06.1: técnico del depósito confirma entrega física por equipo: Entregado Sí/No y observación.
- RF-06.2: registrar obligatoriamente quién entrega y quién recibe.
- RF-06.3: ingresar los equipos recibidos con inventario, tipo, descripción, observaciones, área y departamento de origen, fecha, entregante y receptor.
- RF-06.4: filtrar inventario por departamento, área, fecha, tipo, inventario, modelo, marca y serie.

### RF-07 — Despiece (p. 8)

- RF-07.1: técnico del depósito selecciona equipos por inventario con carga automática de datos.
- RF-07.2: solicitud con fecha y hora sugeridas y participantes adicionales opcionales.
- RF-07.3: jefe de soporte aprueba y confirma fecha/hora.
- RF-07.4: al ejecutar, registrar cada pieza con tipo y campos configurables; marcar equipo como Despiece Realizado.
- RF-07.5: incorporar las piezas al almacén.

### RF-08 — Almacén de piezas (p. 8)

- RF-08.1: buscar/filtrar por tipo, marca, modelo, capacidad, estado, serie y disponibilidad.
- RF-08.2: mostrar campos específicos, equipo de origen, departamento de origen, fecha de ingreso y estado.
- RF-08.3: mostrar stock actual por tipo de pieza.
- RF-08.4: consultar historial de extracción del equipo, solicitud de instalación e instalación final.

### RF-09 — Extracción e instalación (p. 8)

- RF-09.1: técnico solicita extracción indicando tipo, modelo, capacidad y criterios de búsqueda.
- RF-09.2: destino: equipo de cualquier departamento o del propio depósito.
- RF-09.3: aprobación del jefe de soporte técnico.
- RF-09.4: al aprobar, descontar provisionalmente stock y reservar la pieza.
- RF-09.5: técnico registra el inventario exacto del receptor al instalar, cerrando trazabilidad.
- RF-09.6: conservar historial de pieza y equipo receptor.

### RF-10 — Traslado de equipos desde depósito (pp. 8–9)

- RF-10.1: solicitud con equipo, departamento destino, justificación y fecha.
- RF-10.2: aprueba el jefe de soporte técnico.
- RF-10.3: marcar equipo Trasladado y registrar movimiento.

### RF-11 — Reportes y trazabilidad (p. 9)

- RF-11.1: solicitudes filtradas por estado, área, departamento, fecha y tipo de recurso.
- RF-11.2: inventario del depósito con todos sus filtros.
- RF-11.3: por inventario, historial completo de equipo: origen, solicitud, aprobaciones, traslado, despiece, piezas y destino final.
- RF-11.4: equipo origen y equipo de instalación de cada pieza.
- RF-11.5: stock disponible por tipo con todos sus campos.
- RF-11.6: todos los reportes exportables a PDF y Excel.

### RF-12 — Notificaciones (p. 9)

- RF-12.1: notificaciones internas en cada transición relevante; correo opcional.
- RF-12.2: jefe de área recibe solicitudes para aprobación.
- RF-12.3: jefe de departamento recibe aprobación/rechazo de área.
- RF-12.4: técnico recibe aprobación económica.
- RF-12.5: jefes de departamento y área reciben aprobación técnica.
- RF-12.6: técnico recibe aprobación de despiece o extracción.

## Requisitos no funcionales

| Código y fuente | Contenido completo por subapartado | Evidencia futura de cumplimiento |
|---|---|---|
| RNF-01, pp. 9–10 | .1 responsive escritorio/tablet/móvil; .2 validación en tiempo real y errores claros en español; .3 acciones según rol/estado; .4 carga de páginas ≤3 s en red normal; .5 Manual de Identidad Visual UHO | Revisión visual, pruebas por rol y estado, validación y medición de carga; obtener manual |
| RNF-02, pp. 9–10 | .1 HTTPS/TLS; .2 OAuth2/OIDC institucional, sin contraseñas locales; .3 RBAC en cada endpoint; .4 auditoría de todas las acciones con actor, acción, fecha e IP; .5 mitigación OWASP Top 10; .6 cifrado en reposo de datos personales; .7 validación en frontend/backend; .8 limitar tasa en autenticación | Pruebas de autorización, CSRF/XSS/IDOR e importaciones, revisión de TLS/cifrado, auditoría y límites de acceso |
| RNF-03, p. 10 | .1 API REST OpenAPI/Swagger; .2 prever SIGENU y ASSET; .3 JSON, XLSX y CSV para intercambio/importación/exportación; .4 formato de inventario compatible con contabilidad UHO | Contrato API validado, archivos de intercambio y muestras oficiales de inventario; integraciones pendientes de contratos |
| RNF-04, p. 10 | .1 al menos 50 usuarios concurrentes sin degradación perceptible; .2 disponibilidad ≥99% laboral lunes–viernes 08:00–18:00; .3 consultas filtradas de inventario <2 s | Pruebas de carga y evidencia de disponibilidad ≥99% durante un período definido antes de medir, con registros de servicio/caídas y cálculo reproducible; acordar volumen, red, zona horaria, período, política de exclusiones y significado de degradación |
| RNF-05, p. 10 | .1 GitLab UHO o GitHub y actualización sistemática; .2 README, instalación, usuario y API; .3 nuevos tipos sin cambiar código; .4 Docker Compose local; .5 nomencladores CRUD sin valores fijos en código | Historial Git, manuales, añadir tipos desde administración y comprobar despliegue reproducible |
| RNF-06, pp. 10–11 | .1 regulaciones cubanas de datos personales; .2 minimización de datos; .3 auditoría accesible solo al administrador | Revisión institucional de cumplimiento, inventario de datos y pruebas de acceso a logs |

Las referencias legales concretas y su aplicabilidad deben validarse con la institución; este análisis no añade ni interpreta leyes.

## Siete roles y permisos

Fuente: descripción de roles y matriz, pp. 5–6. «Propios» en reportes corresponde al departamento/área respectivamente. La matriz original omite al consultor, pero su descripción sí autoriza lectura de reportes, inventarios y estados. No autoriza acceso a logs (RNF-06.3).

| Rol | Permisos respaldados | Alcance y restricciones |
|---|---|---|
| Administrador del sistema | Todas las funciones; CRUD de nomencladores, usuarios, roles/permisos; logs | Acceso total descrito; conservar validaciones e integridad como propuesta técnica |
| Jefe de departamento | Crear baja, importar Excel/agregar equipos, seguimiento, solicitar movimiento económico, reportes propios | Su departamento; no editar listado tras aprobación técnica |
| Jefe de área | Ver listado/resumen, aprobar o rechazar baja, reportes propios | Departamentos supervisados; rechazo con comentario |
| Técnico de soporte | Agendar/aplicar revisión; confirmar recepción; solicitar/ejecutar despiece, registrar piezas; solicitar extracción, registrar instalación; reportes | Uno por departamento y área y uno global del depósito; RF-06/07 asignan recepción/despiece al técnico del depósito; alcance exacto de lectura pendiente |
| Jefe de soporte técnico | Agendar revisión según matriz; aprobar listado técnico, despiece, extracción y traslado; confirmar entrega y registrar piezas según matriz; reportes | Único a nivel universidad; autoridad técnica global |
| Jefe de Economía | Consultar y procesar solicitudes económicas, aprobar movimiento contable, reportes | Uno por sede; no realiza revisión ni recepción |
| Consultor | Leer reportes, inventarios y estados | Sin escritura; alcance territorial de lectura no definido; sin logs |

Ningún permiso no descrito se considera concedido. RF-10 no identifica quién crea el traslado; debe resolverse antes de implementar esa escritura. La descripción del técnico no equivale a autorizar cualquier técnico a operar en depósito.

Detalle por acción, lectura/modificación, ámbito y preguntas pendientes en [PERMISOS.md](PERMISOS.md). Una autorización explícita del PDF se distingue allí de una restricción territorial todavía no definida; no se inventa un ámbito global por silencio de la fuente.

## Proceso completo y transiciones

Fuente: sección 5, pp. 11–12, y RF-02 a RF-10. Los ocho pasos del PDF agrupan «fase 3–4» como revisión y aprobación técnica.

1. Jefe de departamento prepara Borrador, completa datos generales, importa Excel o agrega equipos, revisa listado sin duplicados y envía: Enviada; notificación al área.
2. Jefe de área revisa listado y resumen; aprueba: Aprobada por Área, o rechaza con comentario: Rechazada. Se notifica al solicitante. El PDF no describe reenvío tras rechazo.
3. Técnico agenda fecha/hora de revisión y registra por equipo procede/no procede y comentario opcional: En Revisión Técnica. Conservar también los equipos no aprobados para historial.
4. Jefe de soporte aprueba listado final: Aprobada Técnicamente. Se informa a departamento/área y se bloquea la edición del listado por el jefe de departamento.
5. Jefe de departamento solicita movimiento económico sin editar equipos: Pendiente Movimiento Economía. Economía de su sede procesa en el sistema contable externo y aprueba: Aprobada por Economía; se avisa a soporte. «En Proceso Económico» está enumerado, pero su disparador no está descrito.
6. Departamento entrega físicamente; técnico del depósito marca entregado Sí/No y observaciones por equipo, registra entregante y receptor obligatorios. Solo los recibidos ingresan al inventario. El PDF indica Recibida en Depósito como estado final, sin definir cierre de recepciones parciales.
7. Opcional: técnico del depósito solicita despiece de uno o varios equipos por inventario, fecha/hora sugeridas y participantes opcionales; jefe de soporte aprueba y confirma agenda. Técnico ejecuta, registra cada pieza y su origen en almacén; marca Despiece Realizado.
8. Técnico busca piezas por criterios y solicita extracción para equipo departamental o del depósito. Jefe de soporte aprueba, reserva pieza y reduce disponibilidad provisionalmente. Técnico instala y registra inventario exacto receptor y fecha; historial enlaza origen, extracción e instalación, tanto para pieza como receptor.

De forma adicional al flujo de baja, RF-10 permite solicitar traslado del equipo del depósito a un departamento con justificación y fecha; jefe de soporte aprueba, equipo queda Trasladado y movimiento conservado. No confundir este traslado de salida con el movimiento contable de entrada de RF-05.

Los reportes reconstruyen los movimientos e instalaciones sin reemplazar la auditoría de seguridad. Notificaciones se generan para los destinatarios RF-12; el correo sigue siendo opcional.

## Requisitos institucionales complementarios (pp. 15–16)

- G-01/G-02: experiencia centrada en usuario y guía según rol/estado.
- G-03/G-04: prevención de vulnerabilidades y OWASP Top 10.
- G-05/G-06/G-07: interoperabilidad SIGENU/ASSET, API REST y estándares JSON/OAuth2/OpenAPI 3.0.
- G-08/G-09/G-10: sostenibilidad/calidad, GitLab UHO o GitHub, protección de datos.
- A-01/A-02/A-03/A-04: identidad y logo UHO, autenticación institucional, responsive, API.
- A-05/A-06/A-07: seguridad, logs de todas las acciones y repositorio actualizado.
- A-08/A-09/A-10: CRUD de todos los nomencladores (incluidos cargos como ejemplo), creación de roles/permisos y entrega en desarrollo UHO o local con Docker.

## Dudas y contradicciones a resolver

| ID | Hallazgo y fuente | Tratamiento para fases futuras |
|---|---|---|
| D-01 | Archivo `referencia.pdf` frente al nombre solicitado `requisitos.pdf` | Analizado el único PDF disponible; confirmar que es la referencia definitiva |
| D-02 | RF-02.6 enumera Rechazada entre estados de avance | Tratar rechazo como rama, propuesta; confirmar reenvío/corrección y transiciones de proceso económico |
| D-03 | RF-06 acepta No entregado pero flujo termina Recibida | Acordar recepciones parciales, pendientes, reintentos y condición de cierre |
| D-04 | Matriz permite al jefe de soporte confirmar entrega/registrar piezas; RF-06/07 describen técnico del depósito | Mantener ambas evidencias, confirmar alcance por rol y ámbito del técnico; consultor omitido en matriz |
| D-05 | RF-09 no define cancelación, caducidad ni devolución de reservas; búsqueda por criterios frente a pieza concreta en modelo | Acordar selección/asignación de unidad y ciclo de reserva; no añadir liberaciones automáticas |
| D-06 | RF-10 no asigna solicitante ni distingue aprobación de salida física | Definir actor, ejecución y restricciones de equipos despiezados |
| D-07 | HTML muestra serie individual con «Stock: 3»; modelo PDF usa pieza individual | Propuesta: unidades individuales y stock agregado; confirmar agrupación visual |
| D-08 | HTML no incluye recepción, traslado, reportes completos ni aprobaciones del jefe de soporte | Diseñar vistas faltantes en fase autorizada conservando lenguaje visual; no omitir funciones del PDF |
| D-09 | Prototipo de despiece añade justificación/velocidad; no ofrece modelo de pieza; almacén omite filtros PDF | Son elementos visuales adicionales o faltantes; no convertir justificación en obligación sin validación; campos configurables cubren velocidad |
| D-10 | PDF propone Laravel o Django y estructura Laravel, herramientas PHP; usuario solicita Django/DRF/Vue/Vite | Elegir stack solicitado; adaptar estructura y seleccionar bibliotecas después |
| D-11 | PDF recomienda JWT; no hay contrato de autenticación, credenciales, claims ni endpoints institucionales | Reservar adaptador OIDC; evaluar sesión/token con contrato institucional; nunca crear contraseñas locales |
| D-12 | No se adjuntan manual visual, formato contable, contratos SIGENU/ASSET ni reglas de datos/retención | Solicitar insumos cuando sean necesarios; ejemplos INV y direcciones HTML no son configuración real |
| D-13 | Unicidad solo dentro de solicitud explícita; equipos receptores pueden no haber pasado por depósito | Acordar unicidad institucional, reingresos, validación del receptor y fuente de inventarios activos |
| D-14 | HTML presenta diferencias entre totales y filas visibles (7 equipos frente a 3 filas; 8 áreas frente a 4 filas) y fechas diferentes para un mismo inventario entre pantallas; no se documenta si los listados son parciales. La fuente de SC7 tiene serie DLT-2017-789 y origen INV-0011980, mientras la de SC9 tiene serie DLT-789 y origen INV-0012345 | No afirmar que las fuentes sean la misma pieza ni que sus estados Reservada/Instalada se contradigan. Tratar cantidades/fechas como ejemplos que requieren coherencia futura; no deducir reglas ni cargar estos datos como reales |
| D-15 | RNF-03 prevé integraciones; G-05 dice garantizarlas; métricas sin volumen/período y normativa sin detalle | Acordar alcance de integraciones, plan de carga/disponibilidad y revisión institucional de privacidad |
| D-16 | Declaración de seis módulos y agrupación diferente en tabla 1.4/HTML; checkbox y selector de revisión pueden divergir | Organizar por capacidades RF; proponer una única decisión procede/no procede por equipo |

No se han resuelto estas dudas mediante supuestos funcionales ocultos. Las propuestas de integridad/estructura aparecen identificadas en [MODELO_DATOS.md](MODELO_DATOS.md) y [ARQUITECTURA.md](ARQUITECTURA.md).
