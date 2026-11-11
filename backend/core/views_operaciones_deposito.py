from drf_spectacular.utils import extend_schema, OpenApiTypes
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models_deposito import EquipoDeposito, MovimientoEquipoDeposito
from .roles import ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE, tiene_rol
from .views_deposito import autorizado, registros, serializar


def comprobar_permiso(usuario, registro):
    if not autorizado(usuario, registro, escritura=True):
        raise PermissionDenied('No puedes gestionar este equipo o no pertenece a tu sede.')


def texto(datos, campo, maximo, obligatorio=False):
    valor = datos.get(campo, '')
    if not isinstance(valor, str) or len(valor.strip()) > maximo or (obligatorio and not valor.strip()):
        raise ValidationError({campo: f'Texto requerido: {obligatorio}. Máximo {maximo} caracteres.'})
    return valor.strip()


class ClasificarEquipoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="clasificarequipoview_post", description="ClasificarEquipoView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        registro = get_object_or_404(registros().select_for_update(of=('self',)), pk=pk)
        comprobar_permiso(request.user, registro)
        if registro.fecha_salida:
            raise ValidationError({'estado': 'No se puede clasificar un equipo retirado.'})
        if not isinstance(request.data, dict):
            raise ValidationError({'detalle': 'Se requiere un objeto JSON.'})
        estado = request.data.get('estado')
        if estado not in EquipoDeposito.Estado.values:
            raise ValidationError({'estado': 'Clasificación no válida.'})
        observaciones = texto(request.data, 'observaciones', 2000)
        registro.estado = estado
        registro.observaciones = observaciones
        registro.save(update_fields=['estado', 'observaciones', 'fecha_actualizacion'])
        return Response(serializar(registro))


class MovimientoEquipoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="movimientoequipoview_get", description="MovimientoEquipoView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request, pk):
        registro = get_object_or_404(registros(), pk=pk)
        if not autorizado(request.user, registro):
            raise PermissionDenied('Sin acceso a este equipo.')
        return Response([{
            'id': m.id, 'tipo': m.tipo, 'ubicacion_anterior': m.ubicacion_anterior,
            'ubicacion_nueva': m.ubicacion_nueva, 'destinatario': m.destinatario,
            'motivo': m.motivo, 'realizado_por': m.realizado_por.username,
            'fecha': m.fecha,
        } for m in registro.movimientos.select_related('realizado_por').all()])

    @extend_schema(operation_id="movimientoequipoview_post", description="MovimientoEquipoView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        registro = get_object_or_404(registros().select_for_update(of=('self',)), pk=pk)
        comprobar_permiso(request.user, registro)
        if registro.fecha_salida:
            raise ValidationError({'equipo': 'Este equipo ya salió del depósito.'})
        if not isinstance(request.data, dict):
            raise ValidationError({'detalle': 'Se requiere un objeto JSON.'})
        tipo = request.data.get('tipo')
        if tipo not in MovimientoEquipoDeposito.Tipo.values:
            raise ValidationError({'tipo': 'Tipo de movimiento no válido.'})
        motivo = texto(request.data, 'motivo', 2000, obligatorio=True)
        nueva = texto(request.data, 'ubicacion_nueva', 150)
        destinatario = texto(request.data, 'destinatario', 200)
        if tipo == MovimientoEquipoDeposito.Tipo.REUBICACION:
            if not nueva or nueva == registro.ubicacion:
                raise ValidationError({'ubicacion_nueva': 'Indica una ubicación nueva y diferente.'})
        else:
            raise ValidationError({'tipo': 'Las salidas requieren una solicitud de traslado aprobada. Usa /api/traslados/.'})
            if registro.estado != EquipoDeposito.Estado.DISPONIBLE:
                raise ValidationError({'estado': 'Solo pueden entregarse equipos clasificados como disponibles.'})
            if not destinatario:
                raise ValidationError({'destinatario': 'Indica quién recibe el equipo.'})
            if not tiene_rol(request.user, ADMINISTRADOR, JEFE_SOPORTE):
                raise PermissionDenied('Solo el jefe de soporte o administrador puede autorizar una salida.')
        movimiento = MovimientoEquipoDeposito.objects.create(
            equipo_deposito=registro, tipo=tipo, ubicacion_anterior=registro.ubicacion,
            ubicacion_nueva=nueva if tipo == MovimientoEquipoDeposito.Tipo.REUBICACION else '',
            destinatario=destinatario if tipo == MovimientoEquipoDeposito.Tipo.SALIDA else '',
            motivo=motivo, realizado_por=request.user,
        )
        if tipo == MovimientoEquipoDeposito.Tipo.REUBICACION:
            registro.ubicacion = nueva
            registro.save(update_fields=['ubicacion', 'fecha_actualizacion'])
        else:
            registro.fecha_salida = timezone.now()
            registro.save(update_fields=['fecha_salida', 'fecha_actualizacion'])
        return Response({'movimiento_id': movimiento.id, 'equipo': serializar(registro)}, status=201)


class ResumenDepositoView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="resumendepositoview_get", description="ResumenDepositoView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request):
        if not tiene_rol(request.user, ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE):
            raise PermissionDenied('No tienes acceso al resumen del depósito.')
        qs = registros()
        visibles = [r for r in qs if autorizado(request.user, r)]
        estados = {clave: 0 for clave in EquipoDeposito.Estado.values}
        salidos = 0
        for registro in visibles:
            if registro.fecha_salida:
                salidos += 1
            else:
                estados[registro.estado] += 1
        return Response({'total_recibidos': len(visibles), 'salidos': salidos,
                         'en_deposito': len(visibles) - salidos, 'por_estado': estados})
