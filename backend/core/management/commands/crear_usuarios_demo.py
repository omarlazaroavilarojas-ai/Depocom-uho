import secrets
import string
from pathlib import Path
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from core.roles import (ADMINISTRADOR, JEFE_DEPARTAMENTO, JEFE_AREA, TECNICO_SOPORTE, JEFE_SOPORTE, JEFE_ECONOMIA, CONSULTOR, crear_grupos_roles)

CUENTAS = (("admin_demo", ADMINISTRADOR), ("solicitante_demo", JEFE_DEPARTAMENTO), ("area_demo", JEFE_AREA), ("tecnico_demo", TECNICO_SOPORTE), ("soporte_demo", JEFE_SOPORTE), ("economia_demo", JEFE_ECONOMIA), ("auditor_demo", CONSULTOR))

class Command(BaseCommand):
    help = 'Crea cuentas ficticias de demostración sin modificar usuarios existentes.'

    def add_arguments(self, parser):
        parser.add_argument('--archivo', help='Archivo local nuevo para guardar credenciales')

    @transaction.atomic
    def handle(self, *args, **options):
        archivo = Path(options['archivo']).resolve() if options['archivo'] else None
        if archivo and archivo.exists():
            raise CommandError('El archivo ya existe. Usa otro nombre para no sobrescribir credenciales.')
        crear_grupos_roles()
        User = get_user_model()
        creadas = []
        for nombre, rol in CUENTAS:
            if User.objects.filter(username=nombre).exists():
                self.stdout.write(f'{nombre}: ya existe, no se modifica')
                continue
            alphabet = string.ascii_letters + string.digits + '!@#'
            clave = ''.join(secrets.choice(alphabet) for _ in range(18))
            usuario = User.objects.create_user(username=nombre, password=clave)
            usuario.groups.add(Group.objects.get(name=rol))
            creadas.append((nombre, rol, clave))
        if archivo:
            archivo.write_text('CREDENCIALES DEMO - NO SUBIR A GITHUB\n' + ''.join(f'{n} | {r} | {c}\n' for n,r,c in creadas), encoding='utf-8')
            self.stdout.write(f'Credenciales nuevas guardadas en {archivo}')
        else:
            for n,r,c in creadas:
                self.stdout.write(f'{n} ({r}): {c}')
            self.stdout.write('Guarda las contraseñas fuera de GitHub.')
        self.stdout.write(self.style.SUCCESS(f'{len(creadas)} usuarios nuevos creados'))
