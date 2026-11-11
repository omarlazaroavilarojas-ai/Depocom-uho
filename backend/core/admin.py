
from django.contrib import admin

from .models import Sede, TipoRecurso, Area, Departamento, Equipo


@admin.register(Sede)
class SedeAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "direccion")
    search_fields = ("nombre", "direccion")


@admin.register(TipoRecurso)
class TipoRecursoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "sede")
    search_fields = ("nombre",)


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "tipo",
        "area",
        "centro_costo",
    )
    search_fields = ("nombre", "centro_costo")

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "no_inventario",
        "tipo_recurso",
        "marca",
        "modelo",
        "departamento",
    )

    search_fields = (
        "no_inventario",
        "marca",
        "modelo",
        "no_serie",
    )

    list_filter = (
        "tipo_recurso",
        "departamento",
    )


from .models_deposito import MovimientoEquipoDeposito
admin.site.register(MovimientoEquipoDeposito)
