from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_alter_historialsolicitud_accion"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RecepcionEquipo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha_recepcion", models.DateTimeField(auto_now_add=True)),
                ("observaciones", models.TextField(blank=True)),
                ("equipo_solicitud", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="recepcion_deposito", to="core.equipoensolicitud")),
                ("recibido_por", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="recepciones_deposito", to=settings.AUTH_USER_MODEL)),
            ],
            options={"verbose_name": "recepción de equipo", "verbose_name_plural": "recepciones de equipos", "ordering": ["-fecha_recepcion", "-id"]},
        ),
        migrations.AlterField(
            model_name="historialsolicitud", name="accion",
            field=models.CharField(choices=[
                ("creacion", "Creación"), ("edicion", "Edición"),
                ("revision", "Revisión técnica"), ("presentacion", "Presentación"),
                ("aprobacion_area", "Aprobación del Área"), ("rechazo_area", "Rechazo del Área"),
                ("aprobacion_tecnica", "Aprobación técnica"),
                ("remision_economia", "Remisión a Economía"),
                ("inicio_economia", "Inicio del proceso económico"),
                ("aprobacion_economia", "Aprobación económica"),
                ("recepcion_deposito", "Recepción en depósito"),
            ], max_length=20, verbose_name="acción"),
        ),
    ]
