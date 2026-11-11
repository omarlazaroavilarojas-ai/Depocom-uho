# Matriz de trazabilidad

Fuente normativa: [referencia.pdf](../referencias/referencia.pdf). IDs SC corresponden a [PANTALLAS.md](PANTALLAS.md). Módulos/entidades son diseño de [ARQUITECTURA.md](ARQUITECTURA.md) y [MODELO_DATOS.md](MODELO_DATOS.md). Política por acción/ámbito en [PERMISOS.md](PERMISOS.md). Todos los RF/RNF están analizados; ninguno se considera implementado o probado en aplicación. Las pruebas siguientes son criterios futuros, no resultados ejecutados. Fases e identificadores de tareas corresponden a la versión corregida de [TODO.md](../../TODO.md): PostgreSQL/Compose/Nginx base en F2, validación final en F9.

| Requisito y subapartados cubiertos | PDF | Pantallas / brechas | Módulo y entidades | Verificación futura / fase |
|---|---|---|---|---|
| RF-01.1–7 | p. 6 | SC10 solo áreas; demás CRUD faltantes | identidad/nomencladores: Usuario, Rol, Permiso, Sede, Área, Departamento, TipoRecurso, TipoPieza | CRUD autorizado, tipos sin cambiar código, campos configurables y ámbito; F2/F3 |
| RF-02.1–7 | pp. 6–7 | SC1; listado/seguimiento no completos | solicitudes: SolicitudBaja, EquipoEnSolicitud | Manual/Excel/plantilla, duplicado rechazado, borrador/envío, listado inmutable para jefe tras aprobación; F4 |
| RF-03.1–4 | p. 7 | SC2, SC0 parcial | solicitudes/notificaciones: Aprobación, Notificación | Área propia, resumen correcto, rechazo exige comentario y aviso al solicitante; F4 |
| RF-04.1–5 | p. 7 | SC3; falta aprobación final jefe soporte | solicitudes: RevisiónTécnica, ItemRevisión, Aprobación | Agendar, checklist y descartados conservados, aprobación solo autorizada y aviso a ambos jefes; F4 |
| RF-05.1–3 | p. 7 | SC4; falta solicitar movimiento desde departamento | solicitudes: SolicitudBaja, MovimientoEconómico, Aprobación, EventoDominio | Petición con listado definitivo y sede histórica; procesamiento externo sin integración inventada; aprobación avisa a soporte; F5.1–3, D-02 |
| RF-06.1–4 | pp. 7–8 | SC5 inventario; recepción ausente | deposito: Recepción, ItemRecepción, InventarioDepósito | Checklist por equipo, responsables obligatorios, solo entregados ingresan, todos los filtros; F5 |
| RF-07.1–5 | p. 8 | SC6; falta aprobación/agenda jefe soporte | despiece: SolicitudDespiece, EquipoDespiece, PiezaAlmacén | Cargar por inventario, aprobar fecha/hora antes de ejecución, piezas con origen y estado final; F6 |
| RF-08.1–4 | p. 8 | SC7; faltan filtros y datos dinámicos | almacen: TipoPieza, PiezaAlmacén, historial | Todos los filtros, atributos configurables, stock disponible e historial individual; F6 |
| RF-09.1–6 | p. 8 | SC8/SC7; aprobación/instalación incompletas | almacen: SolicitudExtracciónPieza, Reserva, ExtracciónAlmacén, Instalación, PiezaAlmacén, Equipo | Pendiente sin reserva/pieza obligatoria; 0..1 reserva por solicitud y 1 pieza por reserva; máximo 1 reserva activa por unidad; instalación con receptor exacto, sin doble descuento; F7.1–4, D-05 |
| RF-10.1–3 | pp. 8–9 | Sin pantalla propia; SC9 muestra historial parcial | traslados: SolicitudTraslado, InventarioDepósito | Solicitud con destino/fecha/justificación, aprobación jefe soporte, marca Trasladado e historial; F7 tras D-06 |
| RF-11.1–6 | p. 9 | SC5/7/9; reportes y búsqueda de pieza incompletos | reportes: Equipo, documentos de origen/movimiento/destino, EventoDominio, EventoEquipo, EventoPieza | Cadena documental equipo/pieza/receptor externo sin exponer logs, filtros completos y PDF/Excel de cada reporte; F8.1–6 |
| RF-12.1–6 | p. 9 | SC0 campana/aviso; bandeja ausente | notificaciones: Notificación, EventoDominio | Destinatarios exactos por transición, persistencia y entrega tras commit, lectura interna; correo solo opcional; base F3.12, integración F4–F8 |
| RNF-01.1–5 | p. 9 | Todas; responsive no validado | frontend, permisos API | Escritorio/tablet/móvil, español, acciones válidas, ≤3 s, manual UHO; F3–F9 |
| RNF-02.1–8 | pp. 9–10 | Todas; autenticación no dibujada | Usuario, Rol, Permiso, AsignaciónRol, RolPermiso, LogAuditoría y todos los endpoints | PERMISOS por acción/ámbito/objeto; AUTH-01 pendiente, OIDC sin contraseña local; TLS, actor/fecha/IP, OWASP, cifrado, validación dual y rate limit; F2–F9 |
| RNF-03.1–4 | p. 10 | SC1/5/7/9; integración no representada | API/adaptadores/importación-exportación | OpenAPI, contratos SIGENU/ASSET, JSON/XLSX/CSV y formato inventario validado con UHO; F2/F4/F8/F9 |
| RNF-04.1–3 | p. 10 | SC5 y todas las consultas | PostgreSQL/API/operación | ≥50 concurrentes y filtros <2 s (F9.3); RNF-04.2 requiere período/ventana/protocolo acordados F2.11, evidencia operativa F9.6 y cálculo reproducible ≥99% al completar período F9.7; no basta monitoreo |
| RNF-05.1–5 | p. 10 | SC10 y todo el producto | estructura modular, documentación y despliegue | Historial GitHub, manuales/API, tipos dinámicos, Compose reproducible, catálogos CRUD; F2/F3/F9 |
| RNF-06.1–3 | pp. 10–11 | SC10 logs | identidad/auditoria/datos | Validación institucional de normativa, minimización y logs solo administrador; F2–F9 |

## Cobertura institucional

| Códigos PDF pp. 15–16 | Relación | Evidencia futura |
|---|---|---|
| G-01/02; A-01/03 | RNF-01, SC0–10 | Flujos guiados, manual visual/logo y responsive |
| G-03/04; A-05/06 | RNF-02 | Pruebas de seguridad y auditoría de acciones |
| G-05/06/07; A-02/04 | RNF-03, RNF-02.2 | Contratos de integración y autenticación, API estándar |
| G-08/09; A-07/10 | RNF-05 | Documentación, repositorio actualizado y entrega Docker |
| G-10 | RNF-06 | Revisión institucional de privacidad |
| A-08/09 | RF-01 | CRUD de nomencladores y roles/permisos |

## Bloqueos de diseño por resolver

D-01–D-16 se registran en [REQUISITOS.md](REQUISITOS.md). Prioridad previa a implementar cada flujo: D-02 estados/rechazo, D-03 recepción parcial, D-04 permisos/ámbitos, D-05 reserva/unidad, D-06 traslado/actor, D-11 contrato de autenticación y D-13 inventario/receptores. D-08/09/14 son brechas/inconsistencias visuales; D-10 queda orientada por el stack solicitado. D-12/15 requieren insumos y acuerdos institucionales. La matriz no implica autorización para avanzar de fase.

D-14 corregida: las fuentes de SC7 y SC9 tienen series/procedencias diferentes, por lo que no prueban estados contradictorios de una misma pieza. Diferencias de totales/filas pueden ser ejemplos parciales, no reglas del sistema. AUTH-01 queda pendiente de contrato y aprobación en F2.9; no se impone JWT ni cookie sin esa decisión. Preguntas adicionales de ámbito histórico, acumulación de roles y lectura de trazabilidad entre áreas constan en PERMISOS, sin respuestas institucionales inventadas.

## Dependencias y evidencias de las correcciones

| Documento / asunto | Preparación y dependencia en TODO | Evidencia futura de aceptación |
|---|---|---|
| MODELO_DATOS — identidad, aprobaciones y ER completo | F2.1–6 → F3.1–2 | Diagrama/diccionario coherentes; migraciones y relaciones probadas en PostgreSQL |
| PERMISOS — siete roles, lectura/modificación y ámbitos | F2.2 → F3.4/F3.10 | Celdas autorizadas y denegaciones probadas por acción/objeto/estado y sede/área/departamento; pendientes no concedidos |
| Entorno PostgreSQL/Compose temprano, RNF-05.4 | F2.12–16 → F2.17–21 → F2.22–23 | Persistencia tras reinicio, arranque limpio y restauración; F9.4 revalida configuración final |
| Movimiento económico e ingreso | F2.1/F2.3 → F5.1–5 | Listado histórico intacto, sede competente, evento/aprobación/recepción y trazabilidad enlazados |
| Despiece y piezas | F3.9/F5.5 → F6.1–6 | Pieza enlazada a equipo/despiece/ingreso con atributos históricos e inventario coherente |
| Cardinalidad extracción/reserva/instalación | F2.4 → F7.1–4 | Solicitud sin pieza asignada válida, reserva concreta al aprobar, concurrencia y receptor exacto probados |
| Trazabilidad frente a auditoría | F3.11 y F5–F7 → F8.1–2 | Eventos enlazan origen y destino; acciones auditadas sin exponer logs a roles lectores |
| JWT/sesión con cookie — AUTH-01 | F2.9 → F3.3 → F9.5 | Decisión registrada y pruebas según contrato real; simulación no acredita integración institucional |
| Disponibilidad RNF-04.2 | F2.11 y F9.4 → F9.6 → F9.7 | Período completo y registros de T/D/huecos; 100 × (T − D) / T ≥99% con protocolo acordado |

RF-01–12 y RNF-01–06 conservan su contenido normativo. Las entidades normalizadas y las restricciones de concurrencia son propuestas de diseño explícitas; ninguna casilla documental equivale a implementación.
