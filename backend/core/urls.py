
from django.urls import path

from .views import (
    estado_api,
    iniciar_csrf,
    sesion_actual,
    iniciar_sesion,
    cerrar_sesion,
    SedeListView,
    SedeDetailView,
    AreaListView,
    AreaDetailView,
    TipoRecursoListView,
    TipoRecursoDetailView,
    DepartamentoListView,
    DepartamentoDetailView,
    EquipoListView,
    EquipoDetailView,
)

from .views_solicitudes import (
    SolicitudBajaListCreateView,
    SolicitudBajaDetailView,
)


from .views_revisiones import (
    RevisionTecnicaDetailView,
    GuardarRevisionTecnicaView,
    IniciarRevisionTecnicaView,
    AprobarRevisionTecnicaView,
)


from .views_historial import HistorialSolicitudListView

from .views_inventario import (
    PiezaDepositoListCreateView,
    PiezaDepositoDetailView,
)

from .views_aprobaciones import (
    PresentarSolicitudView,
    DecisionAreaView,
)

urlpatterns = [
    path(
        "estado/",
        estado_api,
        name="estado-api",
    ),

    path(
        "csrf/",
        iniciar_csrf,
        name="iniciar-csrf",
    ),

    path(
        "sesion/",
        sesion_actual,
        name="sesion-actual",
    ),

    path(
        "login/",
        iniciar_sesion,
        name="iniciar-sesion",
    ),

    path(
        "logout/",
        cerrar_sesion,
        name="cerrar-sesion",
    ),

    path(
        "sedes/",
        SedeListView.as_view(),
        name="lista-sedes",
    ),

    path(
        "tipos-recursos/",
        TipoRecursoListView.as_view(),
        name="lista-tipos-recursos",
    ),

    path(
        "departamentos/",
        DepartamentoListView.as_view(),
        name="lista-departamentos",
    ),

    path(
        "equipos/",
        EquipoListView.as_view(),
        name="lista-equipos",
    ),

    path(
        "equipos/<int:pk>/",
        EquipoDetailView.as_view(),
        name="detalle-equipo",
    ),

    path(
        "solicitudes/",
        SolicitudBajaListCreateView.as_view(),
        name="lista-solicitudes",
    ),

    path(
        "solicitudes/<int:pk>/",
        SolicitudBajaDetailView.as_view(),
        name="detalle-solicitud",
    ),

    path(
        "solicitudes/<int:solicitud_id>/historial/",
        HistorialSolicitudListView.as_view(),
        name="historial-solicitud",
    ),

    path(
        "revisiones/<int:equipo_solicitud_id>/",
        RevisionTecnicaDetailView.as_view(),
        name="detalle-revision",
    ),

    path(
        "revisiones/<int:equipo_solicitud_id>/guardar/",
        GuardarRevisionTecnicaView.as_view(),
        name="guardar-revision",
    ),

    path(
        "inventario/",
        PiezaDepositoListCreateView.as_view(),
        name="lista-inventario",
    ),

    path(
        "inventario/<int:pk>/",
        PiezaDepositoDetailView.as_view(),
        name="detalle-inventario",
    ),
]

urlpatterns += [
    path(
        "solicitudes/<int:pk>/presentar/",
        PresentarSolicitudView.as_view(),
        name="presentar-solicitud",
    ),
    path(
        "solicitudes/<int:pk>/decision-area/",
        DecisionAreaView.as_view(),
        name="decision-area",
    ),
]

urlpatterns += [
    path(
        "solicitudes/<int:pk>/iniciar-revision/",
        IniciarRevisionTecnicaView.as_view(),
        name="iniciar-revision-tecnica",
    ),
    path(
        "solicitudes/<int:pk>/aprobar-revision/",
        AprobarRevisionTecnicaView.as_view(),
        name="aprobar-revision-tecnica",
    ),
]

from .views_economia import (
    RemitirEconomiaView, IniciarProcesoEconomicoView, AprobarEconomiaView,
)

urlpatterns += [
    path("solicitudes/<int:pk>/remitir-economia/", RemitirEconomiaView.as_view(), name="remitir-economia"),
    path("solicitudes/<int:pk>/iniciar-economia/", IniciarProcesoEconomicoView.as_view(), name="iniciar-economia"),
    path("solicitudes/<int:pk>/aprobar-economia/", AprobarEconomiaView.as_view(), name="aprobar-economia"),
]

from .views_recepcion import RecepcionSolicitudView

urlpatterns += [
    path("solicitudes/<int:pk>/recepcion/", RecepcionSolicitudView.as_view(), name="recepcion-solicitud"),
]

from .views_deposito import EquiposDepositoView, EquipoDepositoDetailView
urlpatterns += [
    path('deposito/equipos/', EquiposDepositoView.as_view(), name='deposito-equipos'),
    path('deposito/equipos/<int:pk>/', EquipoDepositoDetailView.as_view(), name='deposito-equipo-detalle'),
]

from .views_operaciones_deposito import ClasificarEquipoView, MovimientoEquipoView, ResumenDepositoView
urlpatterns += [
    path('deposito/equipos/<int:pk>/clasificar/', ClasificarEquipoView.as_view(), name='deposito-clasificar'),
    path('deposito/equipos/<int:pk>/movimientos/', MovimientoEquipoView.as_view(), name='deposito-movimientos'),
    path('deposito/resumen/', ResumenDepositoView.as_view(), name='deposito-resumen'),
]

from .views_reportes import ReporteEquiposCSVView, ReporteMovimientosCSVView
urlpatterns += [
    path('reportes/equipos-deposito.csv', ReporteEquiposCSVView.as_view(), name='reporte-equipos-deposito'),
    path('reportes/movimientos-piezas.csv', ReporteMovimientosCSVView.as_view(), name='reporte-movimientos-piezas'),
]

from .views_ciclo_piezas import (TiposPiezaView, DespiecesView, DecisionDespieceView,
    EjecutarDespieceView, PiezasRecuperadasView, StockPiezasView, ExtraccionesView,
    DecisionExtraccionView, InstalarPiezaView, NotificacionesView)
urlpatterns += [
    path('tipos-piezas/', TiposPiezaView.as_view(), name='tipos-piezas'),
    path('despieces/', DespiecesView.as_view(), name='despieces'),
    path('despieces/<int:pk>/decision/', DecisionDespieceView.as_view(), name='decision-despiece'),
    path('despieces/<int:pk>/ejecutar/', EjecutarDespieceView.as_view(), name='ejecutar-despiece'),
    path('almacen/piezas/', PiezasRecuperadasView.as_view(), name='almacen-piezas'),
    path('almacen/stock/', StockPiezasView.as_view(), name='almacen-stock'),
    path('extracciones/', ExtraccionesView.as_view(), name='extracciones'),
    path('extracciones/<int:pk>/decision/', DecisionExtraccionView.as_view(), name='decision-extraccion'),
    path('extracciones/<int:pk>/instalar/', InstalarPiezaView.as_view(), name='instalar-pieza'),
    path('notificaciones/', NotificacionesView.as_view(), name='notificaciones'),
]

from .views_traslados import TrasladosView, DecisionTrasladoView, EjecutarTrasladoView
urlpatterns += [
    path('traslados/', TrasladosView.as_view(), name='traslados'),
    path('traslados/<int:pk>/decision/', DecisionTrasladoView.as_view(), name='traslado-decision'),
    path('traslados/<int:pk>/ejecutar/', EjecutarTrasladoView.as_view(), name='traslado-ejecutar'),
]

from .views_reportes import ReporteFormatoView
urlpatterns += [
    path('reportes/<str:categoria>.<str:formato>', ReporteFormatoView.as_view(), name='reporte-formato'),
]

# Administración de catálogos: operaciones sobre registros individuales.
urlpatterns += [
    path("sedes/<int:pk>/", SedeDetailView.as_view(), name="sede-detalle"),
    path("areas/", AreaListView.as_view(), name="areas"),
    path("areas/<int:pk>/", AreaDetailView.as_view(), name="area-detalle"),
    path("departamentos/<int:pk>/", DepartamentoDetailView.as_view(), name="departamento-detalle"),
    path("tipos-recursos/<int:pk>/", TipoRecursoDetailView.as_view(), name="tipo-recurso-detalle"),
]
