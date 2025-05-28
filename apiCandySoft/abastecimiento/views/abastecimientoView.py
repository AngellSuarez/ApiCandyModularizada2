# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from ..models.abastecimiento import Abastecimiento
from ..models.insumoAbastecimiento import InsumoAbastecimiento
from ..serializers.abastecimientoSerializer import AbastecimientoSerializer
from ..serializers.abastecimientoConInsumos import AbastecimientoConInsumosSerializer
from ..serializers.insumoAbastecimientoSerializer import InsumoAbastecimientoSerializer

class AbastecimientoViewSet(viewsets.ModelViewSet):
    queryset = Abastecimiento.objects.all().order_by('-fecha_creacion')
    serializer_class = AbastecimientoSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AbastecimientoConInsumosSerializer
        return AbastecimientoSerializer
    
    @action(detail=True, methods=['get'])
    def insumos(self, request, pk=None):
        """Obtener todos los insumos de un abastecimiento específico"""
        abastecimiento = self.get_object()
        insumos = InsumoAbastecimiento.objects.filter(abastecimiento_id=abastecimiento)
        serializer = InsumoAbastecimientoSerializer(insumos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def marcar_reportado(self, request, pk=None):
        """Marcar manualmente un abastecimiento como reportado"""
        abastecimiento = self.get_object()
        
        if abastecimiento.estado == 'Reportado':
            return Response(
                {'error': 'El abastecimiento ya está reportado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Marcar todos los insumos como usados y el abastecimiento como reportado
        with transaction.atomic():
            InsumoAbastecimiento.objects.filter(
                abastecimiento_id=abastecimiento,
                estado='Sin usar'
            ).update(estado='Uso medio')
            
            abastecimiento.estado = 'Reportado'
            abastecimiento.save()
        
        serializer = self.get_serializer(abastecimiento)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sin_reportar(self, request):
        """Obtener todos los abastecimientos sin reportar"""
        abastecimientos = self.queryset.filter(estado='Sin reportar')
        serializer = self.get_serializer(abastecimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def reportados(self, request):
        """Obtener todos los abastecimientos reportados"""
        abastecimientos = self.queryset.filter(estado='Reportado')
        serializer = self.get_serializer(abastecimientos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def agregar_insumos(self, request, pk=None):
        """Agregar múltiples insumos a un abastecimiento"""
        abastecimiento = self.get_object()
        insumos_data = request.data.get('insumos', [])

        if not insumos_data:
            return Response(
                {'error': 'Se requiere una lista de insumos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        insumos_creados = []
        errores = []

        with transaction.atomic():
            for i, insumo_data in enumerate(insumos_data):
                try:
                    insumo_id = insumo_data.get('insumo_id')
                    if not insumo_id:
                        errores.append(f"Insumo {i+1}: ID de insumo requerido")
                        continue
                    
                    data = {
                        'insumo_id': insumo_id,
                        'abastecimiento_id': abastecimiento.id,
                        'cantidad': insumo_data.get('cantidad', 1),
                        'comentario': insumo_data.get('comentario', '')
                    }

                    serializer = InsumoAbastecimientoSerializer(data=data)
                    if serializer.is_valid():
                        insumo_creado = serializer.save()
                        insumos_creados.append(serializer.data)
                    else:
                        errores.append(f"Insumo {i+1}: {serializer.errors}")

                except Exception as e:
                    errores.append(f"Insumo {i+1}: {str(e)}")

        if errores:
            return Response(
                {
                    'errores': errores,
                    'insumos_creados': insumos_creados,
                    'parcialmente_exitoso': len(insumos_creados) > 0
                },
                status=status.HTTP_207_MULTI_STATUS if insumos_creados else status.HTTP_400_BAD_REQUEST
            )

        return Response({
            'mensaje': f'Se agregaron {len(insumos_creados)} insumos exitosamente',
            'insumos_creados': insumos_creados
        })
        
    @transaction.atomic
    def perform_destroy(self, instance):
        for insumo_abast in instance.insumoabastecimiento_set.all():
            if insumo_abast.estado == 'Sin usar':
                insumo = insumo_abast.insumo_id
                insumo.stock += insumo_abast.cantidad
                insumo.save()
            insumo_abast.delete()

        instance.delete()
