from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Sede, Area, Departamento, TipoRecurso, Equipo
from .models_solicitudes import SolicitudBaja, EquipoEnSolicitud
from .models_recepcion import RecepcionEquipo
from .models_deposito import EquipoDeposito, MovimientoEquipoDeposito

class OperacionesDepositoTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser('admin_op', 'admin@example.test', 'pass12345')
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        sede = Sede.objects.create(nombre='Sede test', direccion='Test')
        area = Area.objects.create(nombre='Área test', sede=sede)
        dep = Departamento.objects.create(nombre='Departamento test', tipo='departamento', area=area)
        tipo = TipoRecurso.objects.create(nombre='Computadora')
        equipo = Equipo.objects.create(no_inventario='EQ-TEST-1', tipo_recurso=tipo, departamento=dep)
        solicitud = SolicitudBaja.objects.create(numero='SOL-OP-1', solicitante=self.user, departamento=dep, estado='recibida_deposito')
        asociado = EquipoEnSolicitud.objects.create(solicitud=solicitud, equipo=equipo)
        recepcion = RecepcionEquipo.objects.create(equipo_solicitud=asociado, recibido_por=self.user)
        self.registro = EquipoDeposito.objects.create(recepcion=recepcion)

    def test_clasificacion(self):
        r = self.client.post(f'/api/deposito/equipos/{self.registro.pk}/clasificar/', {'estado': 'disponible'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.registro.refresh_from_db()
        self.assertEqual(self.registro.estado, 'disponible')

    def test_salida_y_bloqueo_duplicado(self):
        self.registro.estado = 'disponible'
        self.registro.save()
        url = f'/api/deposito/equipos/{self.registro.pk}/movimientos/'
        # No debe permitirse una salida directa sin autorización formal.
        r = self.client.post(url, {'tipo': 'salida', 'motivo': 'Reutilización', 'destinatario': 'Laboratorio'}, format='json')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(MovimientoEquipoDeposito.objects.count(), 0)

        # La salida válida pasa por solicitud, aprobación y ejecución.
        destino = self.registro.recepcion.equipo_solicitud.solicitud.departamento
        solicitud = self.client.post('/api/traslados/', {
            'equipo_id': self.registro.pk,
            'departamento_destino_id': destino.pk,
            'justificacion': 'Reutilización en laboratorio',
            'fecha_prevista': '2026-11-20',
        }, format='json')
        self.assertEqual(solicitud.status_code, 201, solicitud.data)
        traslado_id = solicitud.data['id']
        decision = self.client.post(f'/api/traslados/{traslado_id}/decision/', {'aprobar': True}, format='json')
        self.assertEqual(decision.status_code, 200, decision.data)
        ejecucion = self.client.post(f'/api/traslados/{traslado_id}/ejecutar/', {}, format='json')
        self.assertEqual(ejecucion.status_code, 200, ejecucion.data)
        self.registro.refresh_from_db()
        self.assertIsNotNone(self.registro.fecha_salida)
        self.assertEqual(MovimientoEquipoDeposito.objects.count(), 1)
        self.assertEqual(self.client.post(f'/api/traslados/{traslado_id}/ejecutar/', {}, format='json').status_code, 400)
        self.assertEqual(self.client.post(url, {'tipo': 'salida', 'motivo': 'Otra', 'destinatario': 'X'}, format='json').status_code, 400)
        self.assertEqual(MovimientoEquipoDeposito.objects.count(), 1)

    def test_reubicacion(self):
        url = f'/api/deposito/equipos/{self.registro.pk}/movimientos/'
        r = self.client.post(url, {'tipo': 'reubicacion', 'motivo': 'Organización', 'ubicacion_nueva': 'Estante B'}, format='json')
        self.assertEqual(r.status_code, 201)
        self.registro.refresh_from_db()
        self.assertEqual(self.registro.ubicacion, 'Estante B')

    def test_resumen(self):
        self.assertEqual(self.client.get('/api/deposito/resumen/').status_code, 200)

    def test_reporte(self):
        r = self.client.get('/api/reportes/equipos-deposito.csv')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'EQ-TEST-1', r.content)
