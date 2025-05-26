from rest_framework import serializers;
from datetime import date,time, timedelta;
from django.db import models;
from ..models.novedades import Novedades
from usuario.models.manicurista import Manicurista
from decimal import Decimal

from rest_framework import serializers;
from datetime import date,time, timedelta;
from django.db import models;

from ..models.liquidaciones import Liquidacion
from usuario.models.manicurista import Manicurista
from cita.models.cita_venta import CitaVenta

class LiquidacionSerializer(serializers.ModelSerializer):
    manicurista_id = serializers.PrimaryKeyRelatedField(queryset=Manicurista.objects.all())
    manicurista_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Liquidacion
        fields = [
            'id',
            'manicurista_id',
            'FechaInicial',
            'FechaFinal',
            'TotalGenerado',
            'Comision',
            'Local',
            'manicurista_nombre',
        ]

    def get_manicurista_nombre(self, obj):
        return f"{obj.manicurista_id.nombre} {obj.manicurista_id.apellido}"

    def validate_manicurista_id(self, manicurista_id):
        if not manicurista_id:
            raise serializers.ValidationError("El manicurista es requerido")
        return manicurista_id

    def validate(self, data):
        manicurista = data.get('manicurista_id')
        fecha_inicial = data.get('FechaInicial')
        fecha_final = data.get('FechaFinal')

        if not (manicurista and fecha_inicial and fecha_final):
            raise serializers.ValidationError("Debe proporcionar manicurista, fecha inicial y fecha final")

        """ if fecha_final != date.today():
            fecha_final_str = fecha_final.strftime('%Y-%m-%d') if isinstance(fecha_final, date) else str(fecha_final)
            raise serializers.ValidationError({
                "FechaFinal": f"La fecha final debe ser {date.today().strftime('%Y-%m-%d')}, pero se recibió {fecha_final_str}"
            }) """
        
        if fecha_final > date.today():
            raise serializers.ValidationError({
                "FechaFinal": f"La fecha final no puede ser posterior a hoy ({date.today()})"
            })


        
        # Validar que no se solapen fechas con liquidaciones existentes
        solapadas = Liquidacion.objects.filter(
            manicurista_id=manicurista,
            FechaInicial__lte=fecha_final,
            FechaFinal__gte=fecha_inicial
        )

        if solapadas.exists():
            raise serializers.ValidationError("Ya existe una liquidación que se solapa con el rango de fechas seleccionado.")


        citas_venta = CitaVenta.objects.filter(
            manicurista_id=manicurista,
            Fecha__gte=fecha_inicial,
            Fecha__lte=fecha_final
        )

        total_generado = sum(cita.Total for cita in citas_venta)
        data['TotalGenerado'] = total_generado
        data['Comision'] = total_generado * Decimal(0.5)
        data['Local'] = total_generado * Decimal(0.5)

        return data

