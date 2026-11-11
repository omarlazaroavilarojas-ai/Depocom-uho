from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_equipodeposito'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(model_name='equipodeposito', name='fecha_salida', field=models.DateTimeField(blank=True, null=True)),
        migrations.CreateModel(name='MovimientoEquipoDeposito', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('tipo', models.CharField(choices=[('salida', 'Salida definitiva'), ('reubicacion', 'Reubicación interna')], max_length=20)),
            ('ubicacion_anterior', models.CharField(blank=True, max_length=150)),
            ('ubicacion_nueva', models.CharField(blank=True, max_length=150)),
            ('destinatario', models.CharField(blank=True, max_length=200)),
            ('motivo', models.TextField()),
            ('fecha', models.DateTimeField(auto_now_add=True)),
            ('equipo_deposito', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='movimientos', to='core.equipodeposito')),
            ('realizado_por', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='movimientos_equipos_deposito', to=settings.AUTH_USER_MODEL)),
        ], options={'ordering': ['-fecha', '-id']}),
    ]
