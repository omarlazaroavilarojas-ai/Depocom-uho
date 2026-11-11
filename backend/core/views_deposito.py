from drf_spectacular.utils import extend_schema, OpenApiTypes
"""Consulta y ubicación de equipos físicamente recibidos en depósito."""
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .alcance import obtener_perfil
from .models_deposito import EquipoDeposito
from .models_recepcion import RecepcionEquipo
from .roles import ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE, JEFE_ECONOMIA, tiene_rol


def autorizado(usuario, registro, escritura=False):
    if tiene_rol(usuario, ADMINISTRADOR):
        return True
    roles = (JEFE_SOPORTE, TECNICO_SOPORTE) if escritura else (JEFE_SOPORTE, TECNICO_SOPORTE, JEFE_ECONOMIA)
    if not tiene_rol(usuario, *roles):
        return False
    perfil = obtener_perfil(usuario)
    solicitud = registro.recepcion.equipo_solicitud.solicitud
    return bool(perfil and perfil.sede_id and solicitud.departamento_id and
                solicitud.departamento.area.sede_id == perfil.sede_id)


def serializar(registro):
    asociacion = registro.recepcion.equipo_solicitud
    equipo = asociacion.equipo
    return {
        'id': registro.id, 'recepcion_id': registro.recepcion_id,
        'solicitud_id': asociacion.solicitud_id,
        'solicitud_numero': asociacion.solicitud.numero,
        'equipo_id': equipo.id, 'no_inventario': equipo.no_inventario,
        'marca': equipo.marca, 'modelo': equipo.modelo,
        'ubicacion': registro.ubicacion, 'estado': registro.estado,
        'observaciones': registro.observaciones,
        'fecha_salida': registro.fecha_salida,
        'fecha_recepcion': registro.recepcion.fecha_recepcion,
        'fecha_actualizacion': registro.fecha_actualizacion,
    }


def registros():
    return EquipoDeposito.objects.select_related(
        'recepcion__equipo_solicitud__equipo',
        'recepcion__equipo_solicitud__solicitud__departamento__area',
    )


class EquiposDepositoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="equiposdepositoview_get", description="EquiposDepositoView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request):
        if not tiene_rol(request.user, ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE, JEFE_ECONOMIA):
            raise PermissionDenied('No tienes permiso para consultar el depósito.')
        estado = request.query_params.get('estado')
        if estado and estado not in EquipoDeposito.Estado.values:
            raise ValidationError({'estado': 'Estado inválido.'})
        qs = registros()
        activo = request.query_params.get('activo')
        if activo not in (None, 'si', 'no'):
            raise ValidationError({'activo': 'Usa si o no.'})
        if activo == 'si':
            qs = qs.filter(fecha_salida__isnull=True)
        elif activo == 'no':
            qs = qs.filter(fecha_salida__isnull=False)
        if estado:
            qs = qs.filter(estado=estado)
        return Response([serializar(r) for r in qs if autorizado(request.user, r)])


class EquipoDepositoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="equipodepositodetailview_get", description="EquipoDepositoDetailView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request, pk):
        registro = get_object_or_404(registros(), pk=pk)
        if not autorizado(request.user, registro):
            raise PermissionDenied('No tienes acceso a este equipo.')
        return Response(serializar(registro))

    @extend_schema(operation_id="equipodepositodetailview_patch", description="EquipoDepositoDetailView: PATCH.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def patch(self, request, pk):
        registro = get_object_or_404(registros().select_for_update(of=('self',)), pk=pk)
        if not autorizado(request.user, registro, escritura=True):
            raise PermissionDenied('No puedes modificar este equipo.')
        if registro.fecha_salida:
            raise ValidationError({'equipo': 'No se puede modificar un equipo que ya salió.'})
        if not isinstance(request.data, dict):
            raise ValidationError({'detalle': 'Envía un objeto JSON.'})
        permitidos = {'ubicacion', 'observaciones'}
        if not request.data or set(request.data) - permitidos:
            raise ValidationError({'detalle': 'Solo se permite modificar ubicación y observaciones.'})
        for campo, limite in (('ubicacion', 150), ('observaciones', 2000)):
            if campo in request.data:
                valor = request.data[campo]
                if not isinstance(valor, str) or len(valor) > limite:
                    raise ValidationError({campo: f'Debe ser texto de hasta {limite} caracteres.'})
                setattr(registro, campo, valor.strip())
        registro.save(update_fields=[*request.data.keys(), 'fecha_actualizacion'])
        return Response(serializar(registro))
