from django import forms
from django.contrib.auth.models import User
from .models import Rol, User as CustomUser, Modulo, videos, Curso


# REGISTRO USUARIO
class Registro(forms.Form):

    username = forms.CharField(
        required=True,
        min_length=4,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario'
        })
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@gmail.com'
        })
    )

    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )

    password2 = forms.CharField(
        label='Confirmar contraseña',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )

    # VALIDAR USERNAME
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Usuario ya registrado')

        return username

    # VALIDAR EMAIL
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Correo ya registrado')

        return email

    # VALIDAR CONTRASEÑAS
    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password and password2 and password != password2:
            self.add_error('password2', 'Las contraseñas no coinciden')

        return cleaned_data

    # CREAR USUARIO
    def save(self):
        return User.objects.create_user(
            username=self.cleaned_data.get('username'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('password'),
        )


# MODULO FORM
class Modulo_Form(forms.ModelForm):

    class Meta:
        model = Modulo
        fields = [
            'nombre',
            'descripcionModulo',
            'paisModulos',
            'unidadModulos',
            'imagenModulo'
        ]

        labels = {
            'nombre': 'Nombre del módulo',
            'descripcionModulo': 'Descripción del módulo',
            'paisModulos': 'País',
            'unidadModulos': 'Unidad',
            'imagenModulo': 'Imagen Módulo',
        }

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del módulo'
            }),

            'descripcionModulo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5
            }),

            'paisModulos': forms.SelectMultiple(attrs={
                'class': 'form-control',
            }),

            'unidadModulos': forms.SelectMultiple(attrs={
                'class': 'form-control',
            }),

            'imagenModulo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

# IMAGEN MODULO
class imagenModulo(forms.Form):

    imagen = forms.ImageField(
        label="Imagen del Módulo",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        help_text='Suba una imagen en formato PNG o JPG.'
    )

# CURSO FORM
class Curso_Form(forms.ModelForm):

    class Meta:
        model = Curso
        fields = ['nombreCurso']

        labels = {
            'nombreCurso': 'Nombre del Curso',
        }

        widgets = {
            'nombreCurso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del curso'
            }),
        }

# VIDEO FORM
class VideoClase_Form(forms.ModelForm):

    class Meta:
        model = videos
        fields = ['video']

        widgets = {
            'video': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'video/mp4,video/*',
                'onchange': 'preguntasVideoPorDefecto(this)'
            }),
        }

        help_texts = {
            'video': 'Sube un video en formato MP4 o similar.',
        }