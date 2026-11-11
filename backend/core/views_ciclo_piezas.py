from drf_spectacular.utils import extend_schema, OpenApiTypes
"""API del circuito de despiece, almacén, reserva e instalación."""
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Equipo
from .models_deposito import EquipoDeposito
from .models_ciclo_piezas import TipoPieza, SolicitudDespiece, PiezaRecuperada, SolicitudExtraccion, Notificacion
from .roles import ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE, tiene_rol
from .views_deposito import autorizado, registros


def exigir(usuario, *roles):
    if not tiene_rol(usuario, *roles):
        raise PermissionDenied('Tu rol no permite esta operación.')


def cadena(data, nombre, limite=2000, requerida=False):
    valor = data.get(nombre, '')
    if not isinstance(valor, str) or len(valor) > limite or (requerida and not valor.strip()):
        raise ValidationError({nombre: f'Texto inválido; máximo {limite} caracteres.'})
    return valor.strip()


def fecha(data, campo):
    from django.utils.dateparse import parse_datetime
    valor = data.get(campo)
    parsed = parse_datetime(valor) if isinstance(valor, str) else None
    if parsed is None:
        raise ValidationError({campo: 'Fecha y hora ISO 8601 requeridas.'})
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)
    return parsed


def despiece_json(d):
    return {'id': d.pk, 'equipo_deposito_id': d.equipo_id, 'estado': d.estado,
            'fecha_sugerida': d.fecha_sugerida, 'fecha_confirmada': d.fecha_confirmada,
            'solicitante': d.solicitante_id, 'aprobado_por': d.aprobado_por_id,
            'ejecutado_por': d.ejecutado_por_id, 'creado': d.creado,
            'piezas': list(d.piezas.values_list('id', flat=True))}


def pieza_json(p):
    return {'id': p.pk, 'codigo': p.codigo, 'tipo_id': p.tipo_id, 'tipo': p.tipo.nombre,
            'marca': p.marca, 'modelo': p.modelo, 'capacidad': p.capacidad,
            'numero_serie': p.numero_serie, 'descripcion': p.descripcion,
            'atributos': p.atributos, 'estado': p.estado,
            'equipo_origen': p.despiece.equipo.recepcion.equipo_solicitud.equipo.no_inventario,
            'equipo_destino_id': p.equipo_destino_id, 'ingresada': p.ingresada,
            'instalada': p.instalada}


def pieza_autorizada(user, p, escritura=False):
    return autorizado(user, p.despiece.equipo, escritura=escritura)


def avisar(usuario, titulo, mensaje):
    Notificacion.objects.create(usuario=usuario, titulo=titulo, mensaje=mensaje)


class TiposPiezaView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="tipospiezaview_get", description="TiposPiezaView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request):
        return Response(list(TipoPieza.objects.values('id', 'nombre', 'campos_adicionales').order_by('nombre')))

    @extend_schema(operation_id="tipospiezaview_post", description="TiposPiezaView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    def post(self, request):
        exigir(request.user, ADMINISTRADOR)
        nombre = cadena(request.data, 'nombre', 100, True)
        campos = request.data.get('campos_adicionales', [])
        if not isinstance(campos, list) or len(campos) > 30 or not all(isinstance(x, str) and 0 < len(x) <= 80 for x in campos):
            raise ValidationError({'campos_adicionales': 'Se requiere una lista de hasta 30 nombres de campo.'})
        if TipoPieza.objects.filter(nombre__iexact=nombre).exists():
            raise ValidationError({'nombre': 'Este tipo ya existe.'})
        obj = TipoPieza.objects.create(nombre=nombre, campos_adicionales=campos)
        return Response({'id': obj.pk, 'nombre': obj.nombre, 'campos_adicionales': campos}, status=201)


class DespiecesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="despiecesview_get", description="DespiecesView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request):
        exigir(request.user, ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE)
        return Response([despiece_json(d) for d in SolicitudDespiece.objects.select_related('equipo', 'solicitante').all()
                         if autorizado(request.user, d.equipo)])

    @extend_schema(operation_id="despiecesview_post", description="DespiecesView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request):
        exigir(request.user, ADMINISTRADOR, TECNICO_SOPORTE)
        equipo = get_object_or_404(registros().select_for_update(of=('self',)), pk=request.data.get('equipo_deposito_id'))
        if not autorizado(request.user, equipo, escritura=True):
            raise PermissionDenied('Equipo fuera de tu sede.')
        if equipo.fecha_salida:
            raise ValidationError({'equipo': 'El equipo ya salió del depósito.'})
        if SolicitudDespiece.objects.filter(equipo=equipo, estado__in=['pendiente', 'aprobada', 'realizada']).exists():
            raise ValidationError({'equipo': 'Ya existe un despiece vigente para este equipo.'})
        d = SolicitudDespiece.objects.create(equipo=equipo, solicitante=request.user,
            fecha_sugerida=fecha(request.data, 'fecha_sugerida'),
            participantes=cadena(request.data, 'participantes', 1000),
            justificacion=cadena(request.data, 'justificacion', 2000, True))
        return Response(despiece_json(d), status=201)


class DecisionDespieceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="decisiondespieceview_post", description="DecisionDespieceView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        exigir(request.user, ADMINISTRADOR, JEFE_SOPORTE)
        d = get_object_or_404(SolicitudDespiece.objects.select_for_update(), pk=pk)
        if not autorizado(request.user, d.equipo, escritura=True):
            raise PermissionDenied('Equipo fuera de tu sede.')
        if d.estado != 'pendiente':
            raise ValidationError({'estado': 'La solicitud ya fue decidida.'})
        aprobar = request.data.get('aprobar')
        if not isinstance(aprobar, bool):
            raise ValidationError({'aprobar': 'Debe ser verdadero o falso.'})
        d.comentario_decision = cadena(request.data, 'comentario', 2000, not aprobar)
        d.estado = 'aprobada' if aprobar else 'rechazada'
        d.aprobado_por = request.user
        d.fecha_confirmada = fecha(request.data, 'fecha_confirmada') if aprobar else None
        d.save()
        avisar(d.solicitante, 'Decisión sobre despiece', f'Despiece {d.pk}: {d.estado}')
        return Response(despiece_json(d))


class EjecutarDespieceView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="ejecutardespieceview_post", description="EjecutarDespieceView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        exigir(request.user, ADMINISTRADOR, TECNICO_SOPORTE)
        d = get_object_or_404(SolicitudDespiece.objects.select_for_update().select_related('equipo'), pk=pk)
        equipo = get_object_or_404(registros().select_for_update(of=('self',)), pk=d.equipo_id)
        if not autorizado(request.user, equipo, escritura=True):
            raise PermissionDenied('Equipo fuera de tu sede.')
        if d.estado != 'aprobada' or equipo.fecha_salida:
            raise ValidationError({'estado': 'Despiece no aprobado o equipo retirado.'})
        piezas = request.data.get('piezas')
        if not isinstance(piezas, list) or not 1 <= len(piezas) <= 100:
            raise ValidationError({'piezas': 'Indica entre 1 y 100 piezas.'})
        codigos = []
        for item in piezas:
            if not isinstance(item, dict):
                raise ValidationError({'piezas': 'Cada pieza debe ser un objeto.'})
            codigo = cadena(item, 'codigo', 70, True)
            codigos.append(codigo)
            tipo = get_object_or_404(TipoPieza, pk=item.get('tipo_id'))
            atributos = item.get('atributos', {})
            if not isinstance(atributos, dict) or set(atributos) - set(tipo.campos_adicionales):
                raise ValidationError({'atributos': 'Los atributos deben corresponder al tipo de pieza.'})
            if any(not isinstance(v, (str, int, float, bool)) or len(str(v)) > 255 for v in atributos.values()):
                raise ValidationError({'atributos': 'Valores de atributos inválidos.'})
        if len(set(codigos)) != len(codigos) or PiezaRecuperada.objects.filter(codigo__in=codigos).exists():
            raise ValidationError({'codigo': 'Hay códigos de pieza duplicados.'})
        for item in piezas:
            PiezaRecuperada.objects.create(despiece=d, tipo_id=item['tipo_id'], codigo=item['codigo'].strip(),
                marca=cadena(item, 'marca', 150), modelo=cadena(item, 'modelo', 150),
                capacidad=cadena(item, 'capacidad', 100), numero_serie=cadena(item, 'numero_serie', 150),
                descripcion=cadena(item, 'descripcion', 2000), atributos=item.get('atributos', {}),
                estado='disponible' if item.get('utilizable', True) is True else 'no_utilizable')
        d.estado = 'realizada'
        d.ejecutado_por = request.user
        d.ejecutado = timezone.now()
        d.save()
        equipo.estado = EquipoDeposito.Estado.NO_UTILIZABLE
        equipo.save(update_fields=['estado', 'fecha_actualizacion'])
        return Response(despiece_json(d))


class PiezasRecuperadasView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="piezasrecuperadasview_get", description="PiezasRecuperadasView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request):
        exigir(request.user, ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE)
        qs = PiezaRecuperada.objects.select_related('tipo', 'despiece__equipo__recepcion__equipo_solicitud__equipo',
                                                    'despiece__equipo__recepcion__equipo_solicitud__solicitud__departamento__area')
        for filtro in ('estado', 'tipo_id'):
            valor = request.query_params.get(filtro)
            if valor:
                if filtro == 'estado' and valor not in PiezaRecuperada.Estado.values:
                    raise ValidationError({'estado': 'Estado inválido.'})
                qs = qs.filter(**{filtro: valor})
        return Response([pieza_json(p) for p in qs if pieza_autorizada(request.user, p)])


class StockPiezasView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="stockpiezasview_get", description="StockPiezasView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request):
        exigir(request.user, ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE)
        # Filtrar por sede antes de agregar para evitar fugas de datos entre sedes.
        visibles = [p.pk for p in PiezaRecuperada.objects.select_related(
            'despiece__equipo__recepcion__equipo_solicitud__solicitud__departamento__area')
            if pieza_autorizada(request.user, p)]
        return Response(list(PiezaRecuperada.objects.filter(pk__in=visibles, estado='disponible')
                             .values('tipo_id', 'tipo__nombre').annotate(cantidad=Count('id')).order_by('tipo__nombre')))


class ExtraccionesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="extraccionesview_get", description="ExtraccionesView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request):
        exigir(request.user, ADMINISTRADOR, JEFE_SOPORTE, TECNICO_SOPORTE)
        return Response([{'id': s.pk, 'pieza_id': s.pieza_id, 'equipo_destino_id': s.equipo_destino_id,
                          'estado': s.estado, 'solicitante': s.solicitante_id, 'creada': s.creada}
                         for s in SolicitudExtraccion.objects.select_related('pieza__despiece__equipo__recepcion__equipo_solicitud__solicitud__departamento__area')
                         if pieza_autorizada(request.user, s.pieza)])

    @extend_schema(operation_id="extraccionesview_post", description="ExtraccionesView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request):
        exigir(request.user, ADMINISTRADOR, TECNICO_SOPORTE)
        p = get_object_or_404(PiezaRecuperada.objects.select_for_update(), pk=request.data.get('pieza_id'))
        if not pieza_autorizada(request.user, p, escritura=True):
            raise PermissionDenied('Pieza fuera de tu sede.')
        if p.estado != 'disponible':
            raise ValidationError({'pieza': 'La pieza no está disponible.'})
        equipo = get_object_or_404(Equipo, pk=request.data.get('equipo_destino_id'))
        if SolicitudExtraccion.objects.filter(pieza=p, estado__in=['pendiente', 'reservada']).exists():
            raise ValidationError({'pieza': 'Ya tiene una solicitud activa.'})
        s = SolicitudExtraccion.objects.create(pieza=p, equipo_destino=equipo, solicitante=request.user,
                                              motivo=cadena(request.data, 'motivo', 2000, True))
        return Response({'id': s.pk, 'estado': s.estado}, status=201)


class DecisionExtraccionView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="decisionextraccionview_post", description="DecisionExtraccionView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        exigir(request.user, ADMINISTRADOR, JEFE_SOPORTE)
        s = get_object_or_404(SolicitudExtraccion.objects.select_for_update(), pk=pk)
        p = get_object_or_404(PiezaRecuperada.objects.select_for_update(), pk=s.pieza_id)
        if not pieza_autorizada(request.user, p, escritura=True):
            raise PermissionDenied('Pieza fuera de tu sede.')
        if s.estado != 'pendiente':
            raise ValidationError({'estado': 'La solicitud ya fue decidida.'})
        aprobar = request.data.get('aprobar')
        if not isinstance(aprobar, bool):
            raise ValidationError({'aprobar': 'Debe ser verdadero o falso.'})
        if aprobar and p.estado != 'disponible':
            raise ValidationError({'pieza': 'La pieza ya no está disponible.'})
        s.comentario = cadena(request.data, 'comentario', 2000, not aprobar)
        s.estado = 'reservada' if aprobar else 'rechazada'
        s.autorizado_por = request.user
        s.autorizada = timezone.now()
        s.save()
        if aprobar:
            p.estado = 'reservada'
            p.save(update_fields=['estado'])
        avisar(s.solicitante, 'Decisión de extracción', f'Extracción {s.pk}: {s.estado}')
        return Response({'id': s.pk, 'estado': s.estado})


class InstalarPiezaView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="instalarpiezaview_post", description="InstalarPiezaView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    @transaction.atomic
    def post(self, request, pk):
        exigir(request.user, ADMINISTRADOR, TECNICO_SOPORTE)
        s = get_object_or_404(SolicitudExtraccion.objects.select_for_update(), pk=pk)
        p = get_object_or_404(PiezaRecuperada.objects.select_for_update(), pk=s.pieza_id)
        if not pieza_autorizada(request.user, p, escritura=True):
            raise PermissionDenied('Pieza fuera de tu sede.')
        if s.estado != 'reservada' or p.estado != 'reservada':
            raise ValidationError({'estado': 'La pieza debe estar reservada para esta solicitud.'})
        inventario = cadena(request.data, 'no_inventario', 100, True)
        if s.equipo_destino.no_inventario != inventario:
            raise ValidationError({'no_inventario': 'El inventario no coincide con el equipo receptor autorizado.'})
        s.estado = 'instalada'
        s.instalado_por = request.user
        s.instalada = timezone.now()
        s.save()
        p.estado = 'instalada'
        p.equipo_destino = s.equipo_destino
        p.instalada = s.instalada
        p.save(update_fields=['estado', 'equipo_destino', 'instalada'])
        return Response({'id': s.pk, 'estado': s.estado, 'pieza': pieza_json(p)})


class NotificacionesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(operation_id="notificacionesview_get", description="NotificacionesView: GET.", responses=OpenApiTypes.ANY)
    def get(self, request):
        return Response(list(Notificacion.objects.filter(usuario=request.user).values(
            'id', 'titulo', 'mensaje', 'creada', 'leida')[:100]))

    @extend_schema(operation_id="notificacionesview_post", description="NotificacionesView: POST.", request=OpenApiTypes.OBJECT, responses=OpenApiTypes.ANY)
    def post(self, request):
        n = get_object_or_404(Notificacion, pk=request.data.get('id'), usuario=request.user)
        if n.leida is None:
            n.leida = timezone.now()
            n.save(update_fields=['leida'])
        return Response({'id': n.pk, 'leida': n.leida})
