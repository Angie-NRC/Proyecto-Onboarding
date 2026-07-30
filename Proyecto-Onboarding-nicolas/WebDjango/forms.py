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

# FORMS DEL PANEL DE ADMIN
from django.forms import inlineformset_factory
from .models import Examen, PreguntaExamen, OpcionExamen

class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff', 'is_active']
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'is_staff': 'Es Staff (Acceso al panel)',
            'is_active': 'Activo',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nombreUser', 'cargo', 'ROL_idrol', 'paisUser', 'Unidad_idUnidad']
        labels = {
            'nombreUser': 'Nombre completo',
            'cargo': 'Cargo',
            'ROL_idrol': 'Rol',
            'paisUser': 'País',
            'Unidad_idUnidad': 'Unidad',
        }
        widgets = {
            'nombreUser': forms.TextInput(attrs={'class': 'form-control'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'ROL_idrol': forms.Select(attrs={'class': 'form-control'}),
            'paisUser': forms.Select(attrs={'class': 'form-control'}),
            'Unidad_idUnidad': forms.Select(attrs={'class': 'form-control'}),
        }

class ExamenForm(forms.ModelForm):
    class Meta:
        model = Examen
        fields = ['tituloExamen', 'video']
        widgets = {
            'tituloExamen': forms.TextInput(attrs={'class': 'form-control'}),
            'video': forms.Select(attrs={'class': 'form-control'}),
        }

class PreguntaExamenForm(forms.ModelForm):
    class Meta:
        model = PreguntaExamen
        fields = ['textoPregunta']
        widgets = {
            'textoPregunta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pregunta...'}),
        }

class OpcionExamenForm(forms.ModelForm):
    class Meta:
        model = OpcionExamen
        fields = ['textoOpcion', 'opcionCorrecta']
        widgets = {
            'textoOpcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opción...'}),
            'opcionCorrecta': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

PreguntaFormSet = inlineformset_factory(
    Examen, PreguntaExamen, form=PreguntaExamenForm, extra=1, can_delete=True
)

OpcionFormSet = inlineformset_factory(
    PreguntaExamen, OpcionExamen, form=OpcionExamenForm, extra=4, can_delete=True
)

class EditarCursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombreCurso', 'moduloCurso']
        widgets = {
            'nombreCurso': forms.TextInput(attrs={'class': 'form-control'}),
            'moduloCurso': forms.Select(attrs={'class': 'form-control'}),
        }