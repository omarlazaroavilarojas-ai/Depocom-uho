
from django.conf import settings
from django.db import models

from .models import Sede, Area, Departamento


class PerfilInstitucional(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_institucional",
    )

    sede = models.ForeignKey(
        Sede,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="perfiles_institucionales",
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="perfiles_institucionales",
    )

    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="perfiles_institucionales",
    )

    class Meta:
        verbose_name = "perfil institucional"
        verbose_name_plural = "perfiles institucionales"

    def clean(self):
        from django.core.exceptions import ValidationError

        errores = {}

        if self.area_id and self.sede_id:
            if self.area.sede_id != self.sede_id:
                errores["area"] = (
                    "El área no pertenece a la sede indicada."
                )

        if self.departamento_id:
            departamento = self.departamento

            if self.area_id:
                if departamento.area_id != self.area_id:
                    errores["departamento"] = (
                        "El departamento no pertenece al área."
                    )

            if self.sede_id:
                if departamento.area.sede_id != self.sede_id:
                    errores["departamento"] = (
                        "El departamento no pertenece a la sede."
                    )

        if errores:
            raise ValidationError(errores)

    def __str__(self):
        return f"Perfil de {self.usuario.get_username()}"
