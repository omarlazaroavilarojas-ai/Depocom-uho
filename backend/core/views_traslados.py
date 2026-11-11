from drf_spectacular.utils import extend_schema, OpenApiTypes
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Departamento
from .models_deposito import EquipoDeposito, MovimientoEquipoDeposito
from .models_traslados import SolicitudTraslado
from .roles import ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE, tiene_rol
from .views_deposito import autorizado, registros


def serializar(t):
    return {'id': t.pk, 'equipo_id': t.equipo_id, 'departamento_destino_id': t.departamento_destino_id,
            'estado': t.estado, 'justificacion': t.justificacion, 'fecha_prevista': t.fecha_prevista,
            'solicitante_id': t.solicitante_id, 'decidido_por_id': t.decidido_por_id,
            'ejecutado_por_id': t.ejecutado_por_id, 'comentario_decision': t.comentario_decision,
            'creado': t.creado, 'decidido_en': t.decidido_en, 'ejecutado_en': t.ejecutado_en}


class TrasladosView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="trasladosview_get", description="TrasladosView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request):
        if not tiene_rol(request.user, ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE):
            raise PermissionDenied('No autorizado.')
        return Response([serializar(t) for t in SolicitudTraslado.objects.select_related(
            'equipo__recepcion__equipo_solicitud__solicitud__departamento__area').all()
            if autorizado(request.user, t.equipo)])

    @extend_schema(operation_id="trasladosview_post", description="TrasladosView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request):
        if not tiene_rol(request.user, ADMINISTRADOR, TECNICO_SOPORTE, JEFE_SOPORTE):
            raise PermissionDenied('No autorizado.')
        e = get_object_or_404(registros().select_for_update(of=('self',)), pk=request.data.get('equipo_id'))
        if not autorizado(request.user, e, escritura=True):
            raise PermissionDenied('Equipo fuera de tu ámbito.')
        if e.fecha_salida or e.estado != EquipoDeposito.Estado.DISPONIBLE:
            raise ValidationError({'equipo': 'Debe estar disponible y dentro del depósito.'})
        destino = get_object_or_404(Departamento, pk=request.data.get('departamento_destino_id'))
        motivo = request.data.get('justificacion')
        dia = parse_date(request.data.get('fecha_prevista', '')) if isinstance(request.data.get('fecha_prevista'), str) else None
        if not isinstance(motivo, str) or not 1 <= len(motivo.strip()) <= 2000 or not dia:
            raise ValidationError({'detalle': 'Justificación (1-2000 caracteres) y fecha_prevista (AAAA-MM-DD) requeridas.'})
        if SolicitudTraslado.objects.filter(equipo=e, estado__in=['pendiente', 'aprobada']).exists():
            raise ValidationError({'equipo': 'Ya existe un traslado activo.'})
        t = SolicitudTraslado.objects.create(equipo=e, departamento_destino=destino,
            solicitante=request.user, justificacion=motivo.strip(), fecha_prevista=dia)
        return Response(serializar(t), status=201)


class DecisionTrasladoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="decisiontrasladoview_post", description="DecisionTrasladoView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        if not tiene_rol(request.user, ADMINISTRADOR, JEFE_SOPORTE):
            raise PermissionDenied('Solo el jefe de soporte autoriza traslados.')
        t = get_object_or_404(SolicitudTraslado.objects.select_for_update(), pk=pk)
        e = get_object_or_404(registros().select_for_update(of=('self',)), pk=t.equipo_id)
        if not autorizado(request.user, e, escritura=True):
            raise PermissionDenied('Fuera de tu ámbito.')
        if t.estado != 'pendiente' or e.fecha_salida:
            raise ValidationError({'estado': 'Traslado no pendiente o equipo retirado.'})
        aprobar = request.data.get('aprobar')
        comentario = request.data.get('comentario', '')
        if not isinstance(aprobar, bool) or not isinstance(comentario, str) or len(comentario) > 2000 or (not aprobar and not comentario.strip()):
            raise ValidationError({'detalle': 'Indica aprobar como booleano y comentario obligatorio si rechazas.'})
        t.estado = 'aprobada' if aprobar else 'rechazada'
        t.comentario_decision = comentario.strip()
        t.decidido_por = request.user
        t.decidido_en = timezone.now()
        t.save()
        return Response(serializar(t))


class EjecutarTrasladoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="ejecutartrasladoview_post", description="EjecutarTrasladoView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        if not tiene_rol(request.user, ADMINISTRADOR, TECNICO_SOPORTE, JEFE_SOPORTE):
            raise PermissionDenied('No autorizado.')
        t = get_object_or_404(SolicitudTraslado.objects.select_for_update(), pk=pk)
        e = get_object_or_404(registros().select_for_update(of=('self',)), pk=t.equipo_id)
        if not autorizado(request.user, e, escritura=True):
            raise PermissionDenied('Fuera de tu ámbito.')
        if t.estado != 'aprobada' or e.fecha_salida or e.estado != EquipoDeposito.Estado.DISPONIBLE:
            raise ValidationError({'estado': 'El traslado no está aprobado o el equipo no está disponible.'})
        equipo = e.recepcion.equipo_solicitud.equipo
        MovimientoEquipoDeposito.objects.create(equipo_deposito=e, tipo=MovimientoEquipoDeposito.Tipo.SALIDA,
            ubicacion_anterior=e.ubicacion, destinatario=t.departamento_destino.nombre,
            motivo=f'Traslado autorizado #{t.pk}: {t.justificacion}', realizado_por=request.user)
        e.fecha_salida = timezone.now()
        e.save(update_fields=['fecha_salida', 'fecha_actualizacion'])
        equipo.departamento = t.departamento_destino
        equipo.save(update_fields=['departamento'])
        t.estado = 'ejecutada'
        t.ejecutado_por = request.user
        t.ejecutado_en = timezone.now()
        t.save()
        return Response(serializar(t))
