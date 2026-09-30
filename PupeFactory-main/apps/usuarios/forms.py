from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from apps.usuarios.models import CustomUser


class UsuarioRegistroForm(forms.ModelForm):
    """
    Formulario web para el registro de nuevos usuarios clientes en PupeFactory.
    Asegura que el rol asignado sea estrictamente CLIENTE y valida la confirmación
    de contraseña y la unicidad del email y nombre de usuario.
    """
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Mínimo 8 caracteres',
            'required': True,
        }),
        help_text="Usa al menos 8 caracteres combinando letras y números."
    )
    password_confirm = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Repite tu contraseña',
            'required': True,
        })
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Elige tu nombre de usuario',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'tu@email.com',
                'required': True,
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Tu nombre',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Tu apellido',
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError("Este nombre de usuario ya se encuentra registrado.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("El correo electrónico es obligatorio.")
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe una cuenta asociada a este correo electrónico.")
        return email.lower()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', "Las contraseñas no coinciden.")
            else:
                try:
                    validate_password(password)
                except ValidationError as e:
                    self.add_error('password', e)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = CustomUser.Role.CLIENTE  # Rol exclusivo CLIENTE para registro público
        if commit:
            user.save()
        return user
