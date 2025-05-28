from django.shortcuts import render
from rest_framework import  viewsets, status, permissions;
from rest_framework.response import Response;
from rest_framework.decorators import action;
from rest_framework.permissions import AllowAny;

from .models import Marca, Insumo
from .serializer import MarcaSerializer, InsumoSerializer
# Create your views here.

class MarcaViewSet(viewsets.ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer;
    permission_classes = [AllowAny]
    

class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all()
    serializer_class = InsumoSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """
        Retorna todos los insumos que NO están inactivos ni agotados.
        Es decir: solo los que están en estado 'Activo' o 'Bajo'
        """
        insumos_disponibles = self.queryset.filter(estado__in=['Activo', 'Bajo'])
        serializer = self.get_serializer(insumos_disponibles, many=True)
        return Response(serializer.data)