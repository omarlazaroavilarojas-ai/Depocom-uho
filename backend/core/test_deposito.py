from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from .models import Area, Departamento, Equipo, Sede, TipoRecurso
from .models_deposito import EquipoDeposito
from .models_perfiles import PerfilInstitucional
from .models_solicitudes import EquipoEnSolicitud, SolicitudBaja
from .roles import TECNICO_SOPORTE


class DepositoTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser('admin_dep', 'admin@dep.test', 'clave')
        self.tecnico = User.objects.create_user('tec_dep', password='clave')
        self.ajeno = User.objects.create_user('ajeno_dep', password='clave')
        sede = Sede.objects.create(nombre='Sede dep', direccion='Dir')
        otra = Sede.objects.create(nombre='Otra sede', direccion='Dir')
        area = Area.objects.create(nombre='Area dep', sede=sede)
        depto = Departamento.objects.create(nombre='Depto dep', tipo='departamento', area=area)
        tipo = TipoRecurso.objects.create(nombre='PC')
        self.solicitud = SolicitudBaja.objects.create(numero='DEP-001', solicitante=self.admin, departamento=depto, estado='aprobada_economia')
        equipo = Equipo.objects.create(no_inventario='DEP-PC-001', tipo_recurso=tipo, departamento=depto)
        self.asociacion = EquipoEnSolicitud.objects.create(solicitud=self.solicitud, equipo=equipo)
        self.tecnico.groups.add(Group.objects.get_or_create(name=TECNICO_SOPORTE)[0])
        PerfilInstitucional.objects.create(usuario=self.tecnico, sede=sede)
        self.ajeno.groups.add(Group.objects.get_or_create(name=TECNICO_SOPORTE)[0])
        PerfilInstitucional.objects.create(usuario=self.ajeno, sede=otra)

    def recibir(self):
        self.client.force_login(self.admin)
        return self.client.post(f'/api/solicitudes/{self.solicitud.pk}/recepcion/', {'equipo_solicitud_id': self.asociacion.pk}, content_type='application/json')

    def test_recepcion_crea_registro(self):
        self.assertEqual(self.recibir().status_code, 201)
        self.assertEqual(EquipoDeposito.objects.count(), 1)
        self.assertEqual(EquipoDeposito.objects.get().estado, 'pendiente_clasificacion')

    def test_listado_y_ubicacion(self):
        self.recibir()
        self.client.force_login(self.tecnico)
        self.assertEqual(len(self.client.get('/api/deposito/equipos/').json()), 1)
        registro = EquipoDeposito.objects.get()
        url = f'/api/deposito/equipos/{registro.pk}/'
        r = self.client.patch(url, {'ubicacion': 'Estante A-1'}, content_type='application/json')
        self.assertEqual(r.status_code, 200)
        registro.refresh_from_db()
        self.assertEqual(registro.ubicacion, 'Estante A-1')

    def test_sede_ajena_no_ve_ni_modifica(self):
        self.recibir()
        self.client.force_login(self.ajeno)
        self.assertEqual(self.client.get('/api/deposito/equipos/').json(), [])
        self.assertEqual(self.client.patch(f'/api/deposito/equipos/{EquipoDeposito.objects.get().pk}/', {'ubicacion': 'X'}, content_type='application/json').status_code, 403)

    def test_no_permita_cambiar_estado_sin_clasificacion(self):
        self.recibir()
        self.client.force_login(self.admin)
        r = self.client.patch(f'/api/deposito/equipos/{EquipoDeposito.objects.get().pk}/', {'estado': 'disponible'}, content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_anonimo(self):
        self.assertIn(self.client.get('/api/deposito/equipos/').status_code, (401, 403))
