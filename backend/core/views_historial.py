
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models_solicitudes import SolicitudBaja
from .models_historial import HistorialSolicitud
from .serializers_solicitudes import HistorialSolicitudSerializer


class HistorialSolicitudListView(generics.ListAPIView):
    serializer_class = HistorialSolicitudSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        solicitud = get_object_or_404(
            SolicitudBaja,
            pk=self.kwargs["solicitud_id"],
        )

        return HistorialSolicitud.objects.filter(
            solicitud=solicitud
        ).select_related(
            "usuario"
        ).order_by(
            "-fecha",
            "-id",
        )
