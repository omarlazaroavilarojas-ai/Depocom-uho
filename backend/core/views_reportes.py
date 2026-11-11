from drf_spectacular.utils import extend_schema, OpenApiTypes
import csv
from django.http import HttpResponse
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .models_deposito import EquipoDeposito
from .models_movimientos import MovimientoInventario
from .models_inventario import PiezaDeposito
from .models_solicitudes import SolicitudBaja
from .models_historial import HistorialSolicitud
from .models_ciclo_piezas import PiezaRecuperada
from .roles import ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE, JEFE_ECONOMIA, tiene_rol
from .views_deposito import registros, autorizado


def seguro_csv(valor):
    texto = str(valor if valor is not None else '')
    return "'" + texto if texto.lstrip().startswith(('=', '+', '-', '@', '\t', '\r')) else texto


class ReporteEquiposCSVView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(operation_id="reporteequiposcsvview_get", description="ReporteEquiposCSVView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request):
        if not tiene_rol(request.user, ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE, JEFE_ECONOMIA):
            raise PermissionDenied('No autorizado para exportar.')
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="equipos_deposito.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(['Inventario', 'Solicitud', 'Estado', 'Ubicación', 'Recibido', 'Salida'])
        for registro in registros():
            if autorizado(request.user, registro):
                a = registro.recepcion.equipo_solicitud
                writer.writerow([seguro_csv(a.equipo.no_inventario), seguro_csv(a.solicitud.numero),
                                 registro.estado, seguro_csv(registro.ubicacion),
                                 registro.recepcion.fecha_recepcion.isoformat(),
                                 registro.fecha_salida.isoformat() if registro.fecha_salida else ''])
        return response


class ReporteMovimientosCSVView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(operation_id="reportemovimientoscsvview_get", description="ReporteMovimientosCSVView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request):
        if not tiene_rol(request.user, ADMINISTRADOR):
            raise PermissionDenied('Solo administración puede exportar movimientos globales de piezas.')
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="movimientos_piezas.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Código pieza', 'Tipo', 'Cantidad', 'Anterior', 'Posterior', 'Usuario', 'Motivo'])
        for m in MovimientoInventario.objects.select_related('pieza', 'usuario').order_by('-fecha', '-id'):
            writer.writerow([m.fecha.isoformat(), seguro_csv(m.pieza.codigo), m.tipo, m.cantidad,
                             m.existencia_anterior, m.existencia_posterior, seguro_csv(m.usuario.username), seguro_csv(m.motivo)])
        return response


# Exportaciones en formatos de oficina. Se construyen desde los mismos datos y
# reglas de acceso que los reportes CSV para evitar filtraciones entre sedes.
def _datos_equipos(usuario):
    filas = []
    for registro in registros():
        if autorizado(usuario, registro):
            asociacion = registro.recepcion.equipo_solicitud
            filas.append([
                asociacion.equipo.no_inventario, asociacion.solicitud.numero,
                registro.estado, registro.ubicacion,
                registro.recepcion.fecha_recepcion.isoformat(),
                registro.fecha_salida.isoformat() if registro.fecha_salida else '',
            ])
    return ['Inventario', 'Solicitud', 'Estado', 'Ubicación', 'Recibido', 'Salida'], filas


def _datos_movimientos():
    filas = []
    for m in MovimientoInventario.objects.select_related('pieza', 'usuario').order_by('-fecha', '-id'):
        filas.append([
            m.fecha.isoformat(), m.pieza.codigo, m.tipo, m.cantidad,
            m.existencia_anterior, m.existencia_posterior,
            m.usuario.username if m.usuario_id else '', m.motivo,
        ])
    return ['Fecha', 'Código pieza', 'Tipo', 'Cantidad', 'Anterior', 'Posterior', 'Usuario', 'Motivo'], filas


def _xlsx(headers, filas, nombre):
    from io import BytesIO
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    ws = wb.active
    ws.title = 'DepoCom UHO'
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='183153')
    for fila in filas:
        # Impide que valores importados se ejecuten como fórmulas en Excel.
        ws.append([seguro_csv(v) if isinstance(v, str) else v for v in fila])
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    for i, header in enumerate(headers, 1):
        ws.column_dimensions[get_column_letter(i)].width = min(45, max(16, len(header) + 4))
    buffer = BytesIO()
    wb.save(buffer)
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{nombre}.xlsx"'
    return response


def _pdf(headers, filas, nombre, titulo):
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, LongTable, TableStyle
    from xml.sax.saxutils import escape
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=24, rightMargin=24,
                            topMargin=26, bottomMargin=26)
    styles = getSampleStyleSheet()
    usable = landscape(A4)[0] - 48
    widths = [usable / len(headers)] * len(headers)
    def celda(valor):
        texto = escape(str(valor if valor is not None else ''))
        if len(texto) > 110:
            texto = texto[:107] + '…'
        return Paragraph(texto, styles['BodyText'])
    data = [[celda(h) for h in headers]]
    data += [[celda(v) for v in fila] for fila in filas]
    tabla = LongTable(data, colWidths=widths, repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#183153')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F1F4F8')]),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#D0D7E2')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    doc.build([Paragraph(escape(titulo), styles['Title']), Spacer(1, 12), tabla])
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre}.pdf"'
    return response


class ReporteFormatoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="reporteformatoview_get", description="ReporteFormatoView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request, categoria, formato):
        if categoria == 'equipos-deposito':
            if not tiene_rol(request.user, ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE, JEFE_ECONOMIA):
                raise PermissionDenied('No autorizado para exportar equipos.')
            headers, filas = _datos_equipos(request.user)
            nombre, titulo = 'equipos_deposito', 'Inventario del depósito - DepoCom UHO'
        elif categoria == 'movimientos-piezas':
            if not tiene_rol(request.user, ADMINISTRADOR):
                raise PermissionDenied('Solo administración puede exportar movimientos globales.')
            headers, filas = _datos_movimientos()
            nombre, titulo = 'movimientos_piezas', 'Movimientos de piezas - DepoCom UHO'
        elif categoria in ('solicitudes', 'historial-solicitudes', 'trazabilidad-piezas'):
            # Estos reportes contienen datos institucionales de varios departamentos.
            # Se restringen a administración hasta definir políticas de alcance por sede.
            if not tiene_rol(request.user, ADMINISTRADOR):
                raise PermissionDenied('Solo administración puede exportar trazabilidad global.')
            if categoria == 'solicitudes':
                headers = ['Número', 'Estado', 'Departamento', 'Solicitante', 'Creada']
                filas = [[s.numero, s.estado, s.departamento.nombre if s.departamento_id else '',
                          s.solicitante.username, s.fecha_creacion.isoformat()]
                         for s in SolicitudBaja.objects.select_related('departamento', 'solicitante').order_by('-fecha_creacion', '-id')]
                nombre, titulo = 'solicitudes', 'Solicitudes de baja - DepoCom UHO'
            elif categoria == 'historial-solicitudes':
                headers = ['Solicitud', 'Fecha', 'Acción', 'Usuario', 'Descripción']
                filas = [[h.solicitud.numero, h.fecha.isoformat(), h.accion,
                          h.usuario.username, h.descripcion]
                         for h in HistorialSolicitud.objects.select_related('solicitud', 'usuario').order_by('-fecha', '-id')]
                nombre, titulo = 'historial_solicitudes', 'Historial de solicitudes - DepoCom UHO'
            else:
                headers = ['Código', 'Tipo', 'Estado', 'Equipo origen', 'Solicitud despiece',
                           'Equipo destino', 'Ingreso', 'Instalación']
                filas = [[pieza.codigo, pieza.tipo.nombre, pieza.estado,
                          pieza.despiece.equipo.recepcion.equipo_solicitud.equipo.no_inventario,
                          pieza.despiece_id,
                          pieza.equipo_destino.no_inventario if pieza.equipo_destino_id else '',
                          pieza.ingresada.isoformat(),
                          pieza.instalada.isoformat() if pieza.instalada else '']
                         for pieza in PiezaRecuperada.objects.select_related(
                             'tipo', 'despiece__equipo__recepcion__equipo_solicitud__equipo',
                             'equipo_destino').order_by('-ingresada', '-id')]
                nombre, titulo = 'trazabilidad_piezas', 'Trazabilidad de piezas - DepoCom UHO'
        else:
            from django.http import Http404
            raise Http404()
        if formato == 'xlsx':
            return _xlsx(headers, filas, nombre)
        if formato == 'pdf':
            return _pdf(headers, filas, nombre, titulo)
        from django.http import Http404
        raise Http404()
