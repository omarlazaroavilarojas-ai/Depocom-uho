# Fases de desarrollo de DepoCom UHO

Solo está autorizada la corrección documental de F1. F2 y posteriores son planificación: requieren autorización expresa antes de ejecutarse. No se instalan dependencias, configuran servicios, crean aplicaciones ni ejecutan migraciones en esta tarea. Cada casilla futura exige evidencia registrada, no una declaración de intención.

Fuentes: [requisitos](docs/arquitectura/REQUISITOS.md), [modelo](docs/arquitectura/MODELO_DATOS.md), [permisos](docs/arquitectura/PERMISOS.md), [arquitectura](docs/arquitectura/ARQUITECTURA.md) y [matriz](docs/arquitectura/MATRIZ_TRAZABILIDAD.md). Dependencia general F1 → F2 → F3 → F4 → F5 → F6 → F7 → F8 → F9. Dentro de cada fase, ejecutar en orden; no cerrar una tarea que dependa de una pregunta sin resolver.

## F1 — Análisis, auditoría y corrección documental

- [x] Leer PDF completo. Aceptación: RF-01–12, RNF-01–06, roles, flujo, modelo y requisitos institucionales contrastados en 16 páginas.
- [x] Analizar HTML completo. Aceptación: once pantallas SC0–10 y función real showScr documentadas.
- [x] Documentar requisitos, pantallas y brechas. Aceptación: subrequisitos y funciones no dibujadas localizables con fuente.
- [x] Corregir modelo ER. Aceptación: identidad, aprobaciones, recepción, movimiento, equipo, despiece, pieza, reserva, extracción, instalación, notificaciones y auditoría relacionados; solicitud pendiente sin pieza obligatoria.
- [x] Crear matriz detallada de permisos. Aceptación: siete roles, lectura/modificación, ámbitos, prohibiciones y permisos no definidos diferenciados.
- [x] Corregir D-14. Aceptación: SC7/SC9 no se identifican como la misma fuente de poder.
- [x] Documentar AUTH-01 y evidencia RNF-04.2. Aceptación: alternativas sin decisión inventada y cumplimiento medido ≥99% durante período acordado.
- [x] Reordenar plan y trazabilidad. Aceptación: PostgreSQL/Compose en F2 y referencias de fases coherentes.
- [x] Comprobar documentación. Aceptación: enlaces válidos, cobertura RF/RNF/SC conservada y fuentes originales con hashes intactos.
- [ ] Obtener revisión y autorización para F2. Aceptación: instrucción expresa del usuario; entregar correcciones no autoriza desarrollo.

## F2 — Acuerdos y entorno reproducible temprano

Depende de aprobación de F1. Las tareas de infraestructura no autorizan resolver reglas de negocio mediante supuestos.

- [ ] F2.1 Acordar estados/rechazos (D-02). Aceptación: tabla de transiciones, actores, edición y reenvío aprobada.
- [ ] F2.2 Acordar ámbitos/permisos (D-04). Aceptación: celdas pendientes de PERMISOS con decisión o bloqueo explícito; combinación de roles y acceso histórico definidos.
- [ ] F2.3 Acordar recepción parcial (D-03). Aceptación: pendientes, reintentos, responsables y condición de cierre definidos.
- [ ] F2.4 Acordar asignación/reservas (D-05). Aceptación: selección de unidad y tratamiento de excepciones definidos; ausencia de cancelación/caducidad automática confirmada o sustituida por regla aprobada.
- [ ] F2.5 Acordar traslado (D-06). Aceptación: solicitante, aprobación, momento de salida y restricciones de equipo definidos.
- [ ] F2.6 Obtener formato/fuente de inventarios (D-13). Aceptación: muestras verificadas, unicidad y receptor externo definidos.
- [ ] F2.7 Obtener Manual de Identidad UHO. Aceptación: fuente disponible o bloqueo visual registrado; no declarar conformidad sin manual.
- [ ] F2.8 Acordar privacidad. Aceptación: datos mínimos, revisión institucional, cifrado, claves y retención documentados.
- [ ] F2.9 Obtener contrato OIDC y resolver AUTH-01. Aceptación: opción sesión/token aprobada y parámetros institucionales verificados o integración marcada bloqueada; sin login local.
- [ ] F2.10 Acordar alcance SIGENU/ASSET (D-15). Aceptación: contratos/entornos y entregables definidos, o bloqueo explícito sin simular integración final.
- [ ] F2.11 Definir protocolo RNF-04.2. Aceptación: período, zona/ventana laboral, sondas, cálculo, exclusiones y tratamiento de huecos acordados antes de medir.
- [ ] F2.12 Elegir versiones. Aceptación: compatibilidad Python/Django/DRF/Vue/Vite/PostgreSQL/Docker revisada en documentación oficial y versiones fijadas.
- [ ] F2.13 Preparar Git y exclusión de secretos. Aceptación: historial local y reglas de exclusión verificados; GitHub solo con remoto/destino autorizado.
- [ ] F2.14 Preparar configuración de entorno de ejemplo. Aceptación: variables documentadas sin secretos ni valores institucionales inventados.
- [ ] F2.15 Definir Compose mínimo con PostgreSQL. Aceptación: configuración validada, versión fijada, red/volumen y healthcheck declarados.
- [ ] F2.16 Arrancar PostgreSQL y comprobar persistencia. Depende de F2.15. Aceptación: conexión verificada; dato temporal de comprobación persiste tras reinicio del contenedor y se limpia de forma controlada.
- [ ] F2.17 Crear base Django/DRF. Depende de PostgreSQL operativo. Aceptación: arranque y conexión comprobados; no crear modelos de dominio antes de F3.
- [ ] F2.18 Crear base Vue/Vite. Aceptación: compilación y arranque mínimos comprobados.
- [ ] F2.19 Incorporar aplicaciones a Compose. Depende de F2.17–18. Aceptación: entorno limpio levanta frontend/backend/BD con instrucciones reproducibles.
- [ ] F2.20 Preparar Nginx inicial. Depende de F2.19. Aceptación: sirve frontend y enruta API con orígenes/proxy documentados; no usar Vite como servidor de producción.
- [ ] F2.21 Preparar contrato OpenAPI inicial y ejecución de pruebas. Aceptación: esquema accesible y prueba de conexión/API ejecutada con PostgreSQL real.
- [ ] F2.22 Probar backup/restauración inicial de BD. Aceptación: restauración en base aislada conserva datos de prueba; conservar resultado y procedimiento.
- [ ] F2.23 Cerrar entorno base. Aceptación: arranque desde instrucciones en entorno limpio y registro de bloqueos institucionales; solicitar autorización F3.

## F3 — Modelo, identidad, permisos y componentes comunes

Depende de F2; no implementar una política pendiente como si estuviera aprobada.

- [ ] F3.1 Cerrar diccionario y restricciones del modelo. Aceptación: cardinalidades y decisiones F2 reflejadas en modelo/matriz, sin inconsistencias.
- [ ] F3.2 Crear modelos de identidad/organización. Aceptación: migraciones y relaciones probadas en PostgreSQL.
- [ ] F3.3 Implementar integración de autenticación acordada. Aceptación: validaciones/expiración/logout probados según AUTH-01; integración real pendiente hasta verificar entorno institucional.
- [ ] F3.4 Implementar permisos y ámbitos comunes. Aceptación: pruebas por siete roles, objetos y acceso entre sedes/áreas/departamentos pasan.
- [ ] F3.5 Implementar CRUD sedes. Aceptación: crear/leer/editar/borrar o proteger referencias según política acordada, con permisos probados.
- [ ] F3.6 Implementar CRUD áreas. Aceptación: sede/jefe y dependencias validados.
- [ ] F3.7 Implementar CRUD departamentos. Aceptación: área/tipo/centro de costo/jefe y permisos validados.
- [ ] F3.8 Implementar CRUD tipos de recursos. Aceptación: nuevo tipo utilizable sin cambiar código.
- [ ] F3.9 Implementar tipos de pieza/esquemas. Aceptación: campos dinámicos validados y datos históricos preservados al cambiar esquema.
- [ ] F3.10 Implementar gestión usuarios/roles/permisos. Aceptación: sin escalada no autorizada ni contraseñas locales.
- [ ] F3.11 Implementar auditoría y eventos comunes. Aceptación: actor/fecha/IP/objetivo, correlación y acceso exclusivo de logs probados; sin secretos.
- [ ] F3.12 Implementar notificaciones base. Aceptación: persistencia tras transición válida y entrega después de commit probadas.
- [ ] F3.13 Construir layout y componentes de formulario/tabla/timeline/modal. Aceptación: revisión contra HTML, español y responsive registrada.
- [ ] F3.14 Conectar administración SC10. Aceptación: CRUD con datos reales, errores y permisos comprobados.
- [ ] F3.15 Cerrar F3. Aceptación: pruebas previas pasan y documentación actualizada; autorización F4 solicitada.

## F4 — Baja, área y revisión técnica

- [ ] F4.1 Crear solicitud/borrador. Aceptación: campos generales RF-02 validados y ámbito JD probado.
- [ ] F4.2 Agregar/quitar equipos manualmente. Aceptación: datos requeridos y duplicados en solicitud probados.
- [ ] F4.3 Generar plantilla XLSX. Aceptación: columnas RF-02.2 y archivo abrible.
- [ ] F4.4 Importar XLSX. Aceptación: archivo correcto, datos inválidos y duplicados con errores por fila probados.
- [ ] F4.5 Incorporar CSV de importación. Aceptación: formato documentado y validación equivalente según RNF-03.3.
- [ ] F4.6 Enviar baja. Aceptación: transición autorizada y aviso solo al área competente.
- [ ] F4.7 Aprobar/rechazar área. Aceptación: resumen correcto, rechazo sin comentario denegado y notificación al JD.
- [ ] F4.8 Agendar revisión. Aceptación: fecha/hora y actor autorizados persistidos.
- [ ] F4.9 Guardar checklist. Aceptación: procede/no procede y comentario por equipo, incluidos descartados.
- [ ] F4.10 Aprobar listado técnico. Aceptación: JST autorizado, listado final bloqueado para JD y avisos a ambos jefes.
- [ ] F4.11 Conectar SC1/2/3 y aprobación faltante. Aceptación: recorrido de baja real con errores visibles y estados consistentes.
- [ ] F4.12 Cerrar F4. Aceptación: pruebas de flujo/permiso pasan y autorización F5 solicitada.

## F5 — Economía, recepción e inventario

- [ ] F5.1 Crear petición de movimiento. Aceptación: JD propio, sede y listado técnico histórico conservados.
- [ ] F5.2 Implementar procesamiento económico acordado. Aceptación: disparador de En Proceso Económico validado según F2.1, sin integración externa ficticia.
- [ ] F5.3 Aprobar movimiento. Aceptación: Economía por sede, aprobación/evento y aviso a soporte probados.
- [ ] F5.4 Registrar recepción/checklist. Aceptación: Sí/No, observaciones, entregante/receptor obligatorios.
- [ ] F5.5 Ingresar equipos recibidos. Aceptación: solo entregados generan ingreso, reintentos no duplican y regla parcial F2.3 probada.
- [ ] F5.6 Implementar consulta inventario. Aceptación: todos los filtros RF-06.4 y permisos de lectura probados.
- [ ] F5.7 Conectar SC4/5 y recepción/movimiento faltantes. Aceptación: datos reales, aprobaciones y responsables consultables.
- [ ] F5.8 Cerrar F5. Aceptación: pruebas de flujo/ámbitos pasan y autorización F6 solicitada.

## F6 — Despiece y almacén

- [ ] F6.1 Crear solicitud despiece. Aceptación: carga por inventario, participantes y agenda sugerida.
- [ ] F6.2 Aprobar despiece. Aceptación: JST y agenda confirmada; no ejecutar sin aprobación.
- [ ] F6.3 Registrar piezas extraídas. Aceptación: atributos dinámicos y origen por equipo/despiece preservados.
- [ ] F6.4 Finalizar despiece. Aceptación: estado Despiece Realizado, piezas y eventos consistentes.
- [ ] F6.5 Implementar filtros de almacén. Aceptación: tipo/marca/modelo/capacidad/estado/serie/disponibilidad probados.
- [ ] F6.6 Calcular stock por tipo/atributos. Aceptación: agregados coinciden con unidades y no confunden estado físico/disponibilidad.
- [ ] F6.7 Conectar SC6/7 y aprobación faltante. Aceptación: registro/búsqueda con datos reales y permisos correctos.
- [ ] F6.8 Cerrar F6. Aceptación: historial de origen y pruebas pasan; autorización F7 solicitada.

## F7 — Reservas, extracción, instalación y traslado

- [ ] F7.1 Crear extracción pendiente. Aceptación: criterios y ambos destinos admitidos sin exigir pieza asignada ni receptor exacto prematuramente.
- [ ] F7.2 Aprobar/asignar unidad. Aceptación: reserva de una pieza y aprobación atómicas; dos aprobaciones concurrentes no asignan la misma unidad activa.
- [ ] F7.3 Registrar extracción física según regla aprobada. Aceptación: actor/fecha y vínculo a reserva, o decisión documentada de registrar junto a instalación; sin trámite inventado.
- [ ] F7.4 Registrar instalación. Aceptación: reserva válida, inventario exacto receptor y fecha, sin doble descuento de stock; historial de ambos extremos.
- [ ] F7.5 Crear traslado. Aceptación: solicitante aprobado en F2.5 y equipo/destino/justificación/fecha validados.
- [ ] F7.6 Aprobar y registrar traslado. Aceptación: JST autorizado, salida en momento acordado y estado Trasladado con evento.
- [ ] F7.7 Conectar SC8 y vistas faltantes. Aceptación: aprobación/reserva/instalación/traslado verificables por rol.
- [ ] F7.8 Cerrar F7. Aceptación: pruebas concurrentes e integridad pasan; autorización F8 solicitada.

## F8 — Reportes, trazabilidad y cobertura de interfaz

- [ ] F8.1 Consultar historial de equipo. Aceptación: cadena de baja, decisiones, Economía, recepción, despiece y traslado reconstruida con documentos.
- [ ] F8.2 Consultar historial de pieza. Aceptación: origen, reserva/extracción e instalación en receptor interno/externo visibles según ámbito.
- [ ] F8.3 Implementar reporte de bajas. Aceptación: todos los filtros RF-11.1 probados.
- [ ] F8.4 Implementar reportes inventario/stock. Aceptación: filtros/campos de RF-11.2/5 y totales comprobados.
- [ ] F8.5 Exportar reportes PDF. Aceptación: cada reporte coincide con consulta y ámbito autorizados.
- [ ] F8.6 Exportar reportes XLSX y CSV de intercambio. Aceptación: archivos abribles, columnas/filtros coherentes y protección frente a fórmulas probada.
- [ ] F8.7 Completar avisos RF-12. Aceptación: cada destinatario/transición probado; correo solo si se acuerda opción.
- [ ] F8.8 Conectar dashboard SC0. Aceptación: métricas/pendientes/agenda coherentes y acciones autorizadas.
- [ ] F8.9 Conectar SC9 y lectura del consultor. Aceptación: trazabilidad/exportación reales, sin escritura ni logs para consultor.
- [ ] F8.10 Cerrar cobertura visual. Aceptación: once pantallas y flujos faltantes contrastados con HTML/manual disponible.
- [ ] F8.11 Cerrar F8. Aceptación: matriz con evidencias y pruebas completas; autorización F9 solicitada.

## F9 — Validación y entrega

- [ ] F9.1 Ejecutar pruebas de seguridad integrales. Aceptación: permisos/IDOR/CSRF/XSS/importación/rate limit probados y hallazgos resueltos.
- [ ] F9.2 Verificar privacidad/cifrado. Aceptación: mecanismo y claves comprobados, revisión institucional y ausencia de secretos en logs.
- [ ] F9.3 Ejecutar carga RNF-01.4/RNF-04.1/3. Aceptación: ≥50 concurrentes, páginas ≤3 s y filtros <2 s en red/datos acordados.
- [ ] F9.4 Validar despliegue Nginx/Compose. Aceptación: arranque limpio, persistencia, HTTPS y restauración real verificados con configuración final.
- [ ] F9.5 Verificar integración institucional real. Aceptación: AUTH-01/OIDC y alcance SIGENU/ASSET comprobados en entorno autorizado; bloqueos impiden declarar integración cumplida.
- [ ] F9.6 Iniciar medición RNF-04.2. Depende de F9.4 y protocolo F2.11. Aceptación: período inicio/fin fijado y recolección de evidencia operativa en marcha; no marcar requisito cumplido todavía.
- [ ] F9.7 Acreditar disponibilidad RNF-04.2. Depende de F9.6 y período completo. Aceptación: registros/caídas/huecos reconciliados, T laboral y D calculados, 100 × (T − D) / T ≥99%; informe reproducible. Resultado inferior exige corregir y medir nuevo período completo acordado.
- [ ] F9.8 Cerrar manual de instalación. Aceptación: otra ejecución siguiendo instrucciones reproduce entorno y restauración.
- [ ] F9.9 Cerrar manual de usuario y OpenAPI. Aceptación: flujos por rol, rutas/archivos/permisos/errores documentados y contrastados con versión real.
- [ ] F9.10 Auditar matriz final. Aceptación: cada RF/RNF con evidencia de cumplimiento o limitación pendiente explícita; no declarar cumplimiento completo con requisitos sin verificar.
- [ ] F9.11 Entregar versión de tesis. Aceptación: usuario acepta versión identificada en GitHub y evidencia; no cerrar RNF-04.2 por solo tener monitoreo.
