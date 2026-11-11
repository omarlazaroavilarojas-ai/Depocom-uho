from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0011_movimientos_equipos'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(name='TipoPieza', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('nombre', models.CharField(max_length=100, unique=True)),
            ('campos_adicionales', models.JSONField(blank=True, default=list)),
        ]),
        migrations.CreateModel(name='SolicitudDespiece', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('fecha_sugerida', models.DateTimeField()),
            ('participantes', models.TextField(blank=True)),
            ('justificacion', models.TextField()),
            ('estado', models.CharField(choices=[('pendiente','Pendiente'),('aprobada','Aprobada'),('rechazada','Rechazada'),('realizada','Realizada')], default='pendiente', max_length=15)),
            ('fecha_confirmada', models.DateTimeField(blank=True, null=True)),
            ('comentario_decision', models.TextField(blank=True)),
            ('creado', models.DateTimeField(auto_now_add=True)),
            ('ejecutado', models.DateTimeField(blank=True, null=True)),
            ('equipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='despieces', to='core.equipodeposito')),
            ('solicitante', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='despieces_solicitados', to=settings.AUTH_USER_MODEL)),
            ('aprobado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='despieces_aprobados', to=settings.AUTH_USER_MODEL)),
            ('ejecutado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='despieces_ejecutados', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='PiezaRecuperada', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('codigo', models.CharField(max_length=70, unique=True)),
            ('marca', models.CharField(blank=True, max_length=150)),
            ('modelo', models.CharField(blank=True, max_length=150)),
            ('capacidad', models.CharField(blank=True, max_length=100)),
            ('numero_serie', models.CharField(blank=True, max_length=150)),
            ('descripcion', models.TextField(blank=True)),
            ('atributos', models.JSONField(blank=True, default=dict)),
            ('estado', models.CharField(choices=[('disponible','Disponible'),('reservada','Reservada'),('instalada','Instalada'),('no_utilizable','No utilizable')], default='disponible', max_length=20)),
            ('ingresada', models.DateTimeField(auto_now_add=True)),
            ('instalada', models.DateTimeField(blank=True, null=True)),
            ('despiece', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='piezas', to='core.solicituddespiece')),
            ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.tipopieza')),
            ('equipo_destino', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='piezas_instaladas', to='core.equipo')),
        ]),
        migrations.CreateModel(name='SolicitudExtraccion', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('estado', models.CharField(choices=[('pendiente','Pendiente'),('rechazada','Rechazada'),('reservada','Reservada'),('instalada','Instalada'),('cancelada','Cancelada')], default='pendiente', max_length=15)),
            ('motivo', models.TextField()),
            ('comentario', models.TextField(blank=True)),
            ('creada', models.DateTimeField(auto_now_add=True)),
            ('autorizada', models.DateTimeField(blank=True, null=True)),
            ('instalada', models.DateTimeField(blank=True, null=True)),
            ('pieza', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='solicitudes', to='core.piezarecuperada')),
            ('equipo_destino', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='extracciones_destino', to='core.equipo')),
            ('solicitante', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='extracciones_solicitadas', to=settings.AUTH_USER_MODEL)),
            ('autorizado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='extracciones_autorizadas', to=settings.AUTH_USER_MODEL)),
            ('instalado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='extracciones_instaladas', to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name='Notificacion', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('titulo', models.CharField(max_length=160)),
            ('mensaje', models.TextField()),
            ('creada', models.DateTimeField(auto_now_add=True)),
            ('leida', models.DateTimeField(blank=True, null=True)),
            ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones_depocom', to=settings.AUTH_USER_MODEL)),
        ], options={'ordering': ['-creada', '-id']}),
    ]
