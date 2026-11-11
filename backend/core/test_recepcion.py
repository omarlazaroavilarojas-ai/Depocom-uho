from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from .models import Area, Departamento, Equipo, Sede, TipoRecurso
from .models_historial import HistorialSolicitud
from .models_perfiles import PerfilInstitucional
from .models_recepcion import RecepcionEquipo
from .models_solicitudes import EquipoEnSolicitud, SolicitudBaja
from .roles import TECNICO_SOPORTE


class RecepcionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser("admin_recep", "a@prueba.com", "clave")
        self.tecnico = User.objects.create_user("tecnico_recep", password="clave")
        self.ajeno = User.objects.create_user("ajeno_recep", password="clave")
        sede = Sede.objects.create(nombre="Sede A", direccion="Dir")
        otra = Sede.objects.create(nombre="Sede B", direccion="Dir")
        area = Area.objects.create(nombre="Area A", sede=sede)
        dpto = Departamento.objects.create(nombre="Depto A", area=area, tipo=Departamento.Tipo.DEPARTAMENTO)
        tipo = TipoRecurso.objects.create(nombre="PC")
        self.solicitud = SolicitudBaja.objects.create(numero="RECEP-001", solicitante=self.admin, departamento=dpto, estado=SolicitudBaja.Estado.APROBADA_ECONOMIA)
        self.asociaciones = [EquipoEnSolicitud.objects.create(solicitud=self.solicitud, equipo=Equipo.objects.create(no_inventario=f"RECEP-{i}", tipo_recurso=tipo, departamento=dpto)) for i in range(2)]
        self.tecnico.groups.add(Group.objects.get_or_create(name=TECNICO_SOPORTE)[0])
        PerfilInstitucional.objects.create(usuario=self.tecnico, sede=sede)
        PerfilInstitucional.objects.create(usuario=self.ajeno, sede=otra)
        self.url = f"/api/solicitudes/{self.solicitud.id}/recepcion/"

    def recibir(self, usuario, asociacion):
        self.client.force_login(usuario)
        return self.client.post(self.url, {"equipo_solicitud_id": asociacion.id}, content_type="application/json")

    def test_recepcion_parcial(self):
        r = self.recibir(self.tecnico, self.asociaciones[0])
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.json()["pendientes"], 1)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, SolicitudBaja.Estado.APROBADA_ECONOMIA)

    def test_recepcion_completa(self):
        self.recibir(self.tecnico, self.asociaciones[0])
        r = self.recibir(self.tecnico, self.asociaciones[1])
        self.assertEqual(r.status_code, 201)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, SolicitudBaja.Estado.RECIBIDA_DEPOSITO)
        self.assertEqual(RecepcionEquipo.objects.count(), 2)
        self.assertEqual(HistorialSolicitud.objects.filter(solicitud=self.solicitud, accion=HistorialSolicitud.Accion.RECEPCION_DEPOSITO).count(), 2)

    def test_no_duplicar(self):
        self.recibir(self.admin, self.asociaciones[0])
        self.assertEqual(self.recibir(self.admin, self.asociaciones[0]).status_code, 400)

    def test_sin_aprobacion_economica(self):
        self.solicitud.estado = SolicitudBaja.Estado.EN_PROCESO_ECONOMICO
        self.solicitud.save(update_fields=["estado"])
        self.assertEqual(self.recibir(self.admin, self.asociaciones[0]).status_code, 400)

    def test_sin_rol(self):
        self.assertEqual(self.recibir(self.ajeno, self.asociaciones[0]).status_code, 403)

    def test_sede_ajena(self):
        self.tecnico.perfil_institucional.sede = Sede.objects.get(nombre="Sede B")
        self.tecnico.perfil_institucional.save(update_fields=["sede"])
        self.assertEqual(self.recibir(self.tecnico, self.asociaciones[0]).status_code, 403)

    def test_consulta(self):
        self.client.force_login(self.admin)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["total"], 2)

    def test_anonimo(self):
        self.client.logout()
        self.assertIn(self.client.get(self.url).status_code, (401, 403))
