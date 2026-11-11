
from django.db import transaction

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models_inventario import PiezaDeposito
from .permissions import EsSuperusuarioDesarrollo
from .serializers_inventario import PiezaDepositoSerializer
from .servicios_movimientos import registrar_existencia_inicial


class PiezaDepositoListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = PiezaDepositoSerializer

    def get_queryset(self):
        return PiezaDeposito.objects.all().order_by(
            "nombre",
            "id",
        )

    def get_permissions(self):
        if self.request.method == "POST":
            return [EsSuperusuarioDesarrollo()]

        return [IsAuthenticated()]

    @transaction.atomic
    def perform_create(self, serializer):
        pieza = serializer.save()

        registrar_existencia_inicial(
            pieza=pieza,
            cantidad=pieza.cantidad,
            usuario=self.request.user,
        )


class PiezaDepositoDetailView(
    generics.RetrieveUpdateAPIView
):
    serializer_class = PiezaDepositoSerializer

    def get_queryset(self):
        return PiezaDeposito.objects.all()

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [EsSuperusuarioDesarrollo()]

        return [IsAuthenticated()]
