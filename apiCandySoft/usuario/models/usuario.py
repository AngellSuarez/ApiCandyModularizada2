from django.db import models
from django.contrib.auth.models import AbstractUser
from rol.models import Rol;

class Usuario(AbstractUser):
    ESTADOS_CHOICES = (
        ("Activo", "Activo"),
        ("Inactivo", "Inactivo"),
    )

    nombre = models.CharField("nombre", max_length=30, null=False)
    apellido = models.CharField("apellido", max_length=30, null=False)
    correo = models.EmailField("correo", max_length=60, null=False, unique=True)
    estado = models.CharField(max_length=8, choices=ESTADOS_CHOICES, default="Activo")
    rol_id = models.ForeignKey(Rol, on_delete=models.CASCADE)  # Usamos string para evitar dependencia circular

    def __str__(self):
        return self.username

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="api_usuario_groups",
        related_query_name="usuario",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="api_usuario_user_permissions",
        related_query_name="usuario",
    )