from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.usuarios.models import CustomUser
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

# ==============================================================================
# SERIALIZADOR DE AUTENTICACIÓN JWT CON CLAIMS PERSONALIZADOS
# ==============================================================================
# Cumple con el requerimiento de la rúbrica (Criterio 2.2):
# El payload del token JWT debe incluir explícitamente el Rol del usuario,
# además de user_id y username.
# ==============================================================================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializador personalizado para la obtención de pares de tokens (access/refresh).
    Inyecta claims de negocio en el payload del token JWT.
    """

    @classmethod
    def get_token(cls, user: CustomUser):
        token = super().get_token(user)

        # Inclusión de claims personalizados en el payload del JWT
        token['user_id'] = user.id
        token['username'] = user.username
        token['role'] = user.role

        return token

    def validate(self, attrs):
        # Valida credenciales contra el CustomUser y genera access/refresh
        data = super().validate(attrs)

        # Retornamos también los datos del usuario en el cuerpo de la respuesta
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
        }

        return data


class RegistroSerializer(serializers.ModelSerializer):
    """
    Serializador para el registro de nuevos usuarios clientes vía API REST.
    Crea el usuario con rol CLIENTE y hashea la contraseña de forma segura.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True, allow_blank=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'password_confirm', 'role']
        read_only_fields = ['id', 'role']

    def validate_username(self, value):
        if CustomUser.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está registrado.")
        return value

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("El correo electrónico es obligatorio.")
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe una cuenta con este correo electrónico.")
        return value.lower()

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        try:
            validate_password(attrs['password'], CustomUser(
                username=attrs.get('username', ''), email=attrs.get('email', ''),
                first_name=attrs.get('first_name', ''), last_name=attrs.get('last_name', '')))
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': exc.messages})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(
            role=CustomUser.Role.CLIENTE,
            password=password,
            **validated_data
        )
        return user

