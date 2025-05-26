from rest_framework import serializers
from ..models.usuario import Usuario
from rol.models import Rol
from django.contrib.auth.password_validation import validate_password

class UsuarioSerializer(serializers.ModelSerializer):
    rol_id_out = serializers.SerializerMethodField(read_only=True)
    rol_id = serializers.PrimaryKeyRelatedField(queryset=Rol.objects.all())

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'password', 'nombre', 'apellido', 'correo', 'estado', 'rol_id', 'rol_id_out']
        # Hacer que la contraseña solo se pueda escribir y no leer
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }

    def get_rol_id_out(self, obj):
        return obj.rol_id.nombre if obj and obj.rol_id else None

    def validate_rol_id(self, rol_id):
        # Verifica que el rol exista
        try:
            Rol.objects.get(id=rol_id.id)
        except Rol.DoesNotExist:
            raise serializers.ValidationError("El rol no existe")
        return rol_id

    def validate_estado(self, estado):
        # Valida que el estado sea uno de los permitidos
        estados_validos = [choice[0] for choice in Usuario.ESTADOS_CHOICES]
        if estado not in estados_validos:
            raise serializers.ValidationError(f"Estado no válido. Opciones permitidas: {estados_validos}")
        return estado

    def validate_password(self, password):
        # Valida la fortaleza de la contraseña solo si está presente
        if password:
            try:
                validate_password(password)
            except Exception as e:
                raise serializers.ValidationError(str(e))
        return password

    def create(self, validated_data):
        # Crea un nuevo usuario con contraseña encriptada
        password = validated_data.pop('password', None)
        instance = Usuario(**validated_data)

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance

    def update(self, instance, validated_data):
        # Elimina el campo password de los datos validados si no está presente
        password = validated_data.pop('password', None)

        # Si se proporciona una nueva contraseña, se actualiza
        if password:
            instance.set_password(password)

        # Actualiza los demás campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance