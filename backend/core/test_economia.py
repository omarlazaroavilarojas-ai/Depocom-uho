from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from .models import Sede, Area, Departamento
from .models_perfiles import PerfilInstitucional
from .models_historial import HistorialSolicitud
from .models_solicitudes import SolicitudBaja
from .roles import JEFE_SOPORTE, JEFE_ECONOMIA


class EconomiaTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_superuser("admin_econ", "admin_econ@example.com", "testpass")
        self.economia = User.objects.create_user("economia", password="testpass")
        self.soporte = User.objects.create_user("soporte", password="testpass")
        self.otro = User.objects.create_user("otro", password="testpass")
        self.sede = Sede.objects.create(nombre="Sede principal", direccion="Prueba")
        area = Area.objects.create(nombre="Área económica", sede=self.sede)
        departamento = Departamento.objects.create(nombre="Departamento", tipo=Departamento.Tipo.DEPARTAMENTO, area=area)
        self.solicitud = SolicitudBaja.objects.create(
            numero="ECON-001", solicitante=self.admin, departamento=departamento,
            estado=SolicitudBaja.Estado.APROBADA_TECNICAMENTE,
        )
        self.base = f"/api/solicitudes/{self.solicitud.pk}/"
        self.economia.groups.add(Group.objects.get_or_create(name=JEFE_ECONOMIA)[0])
        self.soporte.groups.add(Group.objects.get_or_create(name=JEFE_SOPORTE)[0])
        PerfilInstitucional.objects.create(usuario=self.economia, sede=self.sede)
        PerfilInstitucional.objects.create(usuario=self.soporte, sede=self.sede)

    def post(self, user, accion, datos=None):
        self.client.force_login(user)
        return self.client.post(self.base + accion + "/", data=datos or {}, content_type="application/json")

    def test_flujo_completo_y_auditoria(self):
        self.assertEqual(self.post(self.soporte, "remitir-economia").status_code, 200)
        self.assertEqual(self.post(self.economia, "iniciar-economia").status_code, 200)
        self.assertEqual(self.post(self.economia, "aprobar-economia", {"comentario": "Documentación revisada"}).status_code, 200)
        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado, SolicitudBaja.Estado.APROBADA_ECONOMIA)
        self.assertEqual(HistorialSolicitud.objects.filter(solicitud=self.solicitud).count(), 3)

    def test_no_saltar_etapas(self):
        self.assertEqual(self.post(self.economia, "aprobar-economia").status_code, 400)
        self.assertEqual(self.post(self.economia, "iniciar-economia").status_code, 400)

    def test_usuario_sin_rol_denegado(self):
        self.assertEqual(self.post(self.otro, "remitir-economia").status_code, 403)
        self.assertEqual(self.post(self.otro, "iniciar-economia").status_code, 403)

    def test_no_repetir_transicion(self):
        self.assertEqual(self.post(self.soporte, "remitir-economia").status_code, 200)
        self.assertEqual(self.post(self.soporte, "remitir-economia").status_code, 400)

    def test_otra_sede_denegada(self):
        otra = Sede.objects.create(nombre="Otra sede", direccion="Otra")
        perfil = PerfilInstitucional.objects.get(usuario=self.economia)
        perfil.sede = otra
        perfil.save()
        self.assertEqual(self.post(self.soporte, "remitir-economia").status_code, 200)
        self.assertEqual(self.post(self.economia, "iniciar-economia").status_code, 403)

    def test_anonimo_no_puede_aprobar(self):
        self.client.logout()
        self.assertIn(self.client.post(self.base + "aprobar-economia/").status_code, (401, 403))
