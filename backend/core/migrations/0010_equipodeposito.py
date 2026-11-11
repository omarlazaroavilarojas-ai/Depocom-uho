from django.db import migrations, models
import django.db.models.deletion


def completar_recepciones(apps, schema_editor):
    Recepcion = apps.get_model('core', 'RecepcionEquipo')
    Registro = apps.get_model('core', 'EquipoDeposito')
    for recepcion in Recepcion.objects.using(schema_editor.connection.alias).all().iterator():
        Registro.objects.using(schema_editor.connection.alias).get_or_create(recepcion_id=recepcion.pk)


class Migration(migrations.Migration):
    dependencies = [('core', '0009_recepcionequipo')]
    operations = [
        migrations.CreateModel(
            name='EquipoDeposito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ubicacion', models.CharField(blank=True, max_length=150)),
                ('estado', models.CharField(choices=[('pendiente_clasificacion', 'Pendiente de clasificación'), ('revision', 'En revisión'), ('disponible', 'Disponible'), ('no_utilizable', 'No utilizable')], default='pendiente_clasificacion', max_length=30)),
                ('observaciones', models.TextField(blank=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('recepcion', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='registro_deposito', to='core.recepcionequipo')),
            ],
            options={'ordering': ['-recepcion__fecha_recepcion', '-id'], 'verbose_name': 'equipo del depósito', 'verbose_name_plural': 'equipos del depósito'},
        ),
        migrations.RunPython(completar_recepciones, migrations.RunPython.noop),
    ]
