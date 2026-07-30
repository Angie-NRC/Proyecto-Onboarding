from django.db import models
from .validators import duracion_video

# MODEL ROL USUARIOS 
class Rol(models.Model):
    rol=models.CharField(max_length=45)
    def __str__(self):
        return self.rol
    
# MODEL PARA USUARIOS 
class User(models.Model):
    nombreUser=models.CharField(max_length=45)
    cargo=models.CharField(max_length=45)
    ROL_idrol=models.ForeignKey("Rol", on_delete=models.CASCADE, null=True, blank=True)
    paisUser=models.ForeignKey("Pais", on_delete=models.CASCADE, null=True, blank=True )
    Unidad_idUnidad=models.ForeignKey("Unidad", on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return self.nombreUser

# MODEL PARA PAISES 
class Pais(models.Model):
    nombrePais=models.CharField(max_length=45)
    def __str__(self):
        return self.nombrePais
    
# MODEL PARA UNIDADES(EJ: ICT )
class Unidad(models.Model):
    nombreUnidad=models.CharField(max_length=45)
    paises = models.ManyToManyField(Pais) 
    icono = models.ImageField(upload_to='iconos_unidades/', null=True, blank=True)

    def __str__(self):
        return self.nombreUnidad


# RUTAS DE LOS VIDEOS DE CADA CURSO 
def rutasImagenes(instance, filename):
    modulo_nombre = instance.nombre if instance.nombre else "ModuloSinNombre"
    modulo_nombre = modulo_nombre.replace(" ", "_")
    return f"WebDjango/{modulo_nombre}/{filename}"


# MODEL PARA MODULOS(ACA ESTOS CONTIENEN LOS CURSOS )
class Modulo(models.Model):
    nombre=models.CharField(max_length=250,  null=True, blank=True)
    descripcionModulo = models.CharField(max_length=550)
    paisModulos= models.ManyToManyField('Pais', blank=True)
    unidadModulos= models.ManyToManyField('Unidad', blank=True)
    imagenModulo =  models.ImageField( upload_to=rutasImagenes, null=False, blank=False
    )
    def __str__(self):
        return self.nombre
    
# MODEL CURSOS QUE EL USUARIO VE 
class Curso(models.Model):
    nombreCurso = models.CharField(max_length=45)
    moduloCurso = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    def __str__(self):
        return self.nombreCurso

    

# CONTENIDOS QUE ESTAN ALOJADOS EN LA APLICACION 

# RUTAS DE LOS VIDEOS DE CADA CURSO 
def rutasVideos(instance, filename):
    return  f"WebDjango/Modulo_{instance.curso.id}/{filename}"

class videos(models.Model):
    nombreVideo = models.CharField(max_length=100) 
    video = models.FileField(upload_to=rutasVideos, validators=[duracion_video])
    curso = models.ForeignKey("Curso", on_delete=models.CASCADE,related_name="videos")
    ordenVideos= models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.nombreVideo


from django.db import migrations, models



# EXAMEN 
class Examen(models.Model):
    video = models.OneToOneField(videos,
        on_delete=models.CASCADE,
        related_name="examen"
    )
    tituloExamen = models.CharField(max_length=200)

    def __str__(self):
        return self.tituloExamen

# PREGUNTAS DEL EXAMEN  
class PreguntaExamen(models.Model): 
    examen = models.ForeignKey(Examen,on_delete=models.CASCADE,related_name="preguntas")
    textoPregunta = models.CharField(max_length=500)
    def __str__(self):
        return self.textoPregunta

# OPCIONES DE RESPUESTA DEL EXAMEN 
class OpcionExamen(models.Model):
    pregunta = models.ForeignKey(
        PreguntaExamen,
        on_delete=models.CASCADE,
        related_name="opciones"
    )
    textoOpcion = models.CharField(max_length=600)
    opcionCorrecta = models.BooleanField(default=False)

    def __str__(self):
        return self.textoOpcion

# RESULTADO DEL USUARIO CUESTIONARIO
class ResultadoCuestionario(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    examen = models.ForeignKey(
        Examen,
        on_delete=models.CASCADE
    )

    puntaje = models.PositiveIntegerField()

    aprobado = models.BooleanField(
        default=False
    )

    intento = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        unique_together = (
            "usuario",
            "examen",
            "intento"
        )


# PROGRESO DEL CURSO
class ProgresoCurso(models.Model):

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE
    )

    ultimo_video = models.ForeignKey(
        videos,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="progreso"
    )

    class Meta:
        unique_together = (
            "usuario",
            "curso"
        )

    def __str__(self):
        return (
            f"{self.usuario.nombreUser} - "
            f"{self.curso.nombreCurso}"
        )