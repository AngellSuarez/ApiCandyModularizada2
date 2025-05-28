from rest_framework import serializers;
from .models import Insumo, Marca;

class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca;
        fields = '__all__';
        # fields = ['id', 'nombre'];
        
    def validate_nombre(self,nombre):
        if not nombre:
            raise serializers.ValidationError("El nombre es requerido");
        if len(nombre)<3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres");
        if nombre.isdigit():
            raise serializers.ValidationError("El nombre no puede contener solo numeros");
        return nombre;
        
class InsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insumo;
        fields = 'id, nombre, stock, marca_id, estado, marca_nombre'.split(', ');
    marca_nombre = serializers.SerializerMethodField();
        
    def get_marca_nombre(self, obj):
        return obj.marca_id.nombre if obj.marca_id else None;
        
    def validate_nombre(self,nombre):
        if not nombre:
            raise serializers.ValidationError("El nombre es requerido");
        if len(nombre)<3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres");
        if nombre.isdigit():
            raise serializers.ValidationError("El nombre no puede contener solo numeros");
        
        return nombre;
    def validate_stock(self,stock):
        if stock < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa");
        return stock;
        
    def validate_marca(self,marca_id):
        if not marca_id:
            raise serializers.ValidationError("La marca es requerida");
            
        try:
            Marca.objects.get(id=marca_id);
        except Marca.DoesNotExist:
            raise serializers.ValidationError("La marca no existe");
        return marca_id;