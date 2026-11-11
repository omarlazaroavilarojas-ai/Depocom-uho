from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('core', '0012_ciclo_piezas'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name='SolicitudTraslado', fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('justificacion', models.TextField()),
        ('fecha_prevista', models.DateField()),
        ('estado', models.CharField(max_length=12, choices=[('pendiente','Pendiente'),('aprobada','Aprobada'),('rechazada','Rechazada'),('ejecutada','Ejecutada')], default='pendiente')),
        ('comentario_decision', models.TextField(blank=True)),
        ('decidido_en', models.DateTimeField(blank=True, null=True)),
        ('ejecutado_en', models.DateTimeField(blank=True, null=True)),
        ('creado', models.DateTimeField(auto_now_add=True)),
        ('equipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='solicitudes_traslado', to='core.equipodeposito')),
        ('departamento_destino', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='traslados_recibidos', to='core.departamento')),
        ('solicitante', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='traslados_solicitados', to=settings.AUTH_USER_MODEL)),
        ('decidido_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='traslados_decididos', to=settings.AUTH_USER_MODEL)),
        ('ejecutado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='traslados_ejecutados', to=settings.AUTH_USER_MODEL)),
    ], options={'ordering': ['-creado', '-id']})]
