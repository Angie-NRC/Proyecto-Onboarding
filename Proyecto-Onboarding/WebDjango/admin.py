from django.contrib import admin
from .models import (
    Rol,
    User,
    Unidad,
    Pais,
    Modulo,
    Curso,
    videos,
    Examen,
    ResultadoCuestionario, 
    OpcionExamen, 
    PreguntaExamen


)

admin.site.register(Rol)
admin.site.register(User)
admin.site.register(Unidad)
admin.site.register(Pais)
admin.site.register(Modulo)
admin.site.register(Curso)
admin.site.register(videos)
admin.site.register(Examen)
admin.site.register(ResultadoCuestionario)
admin.site.register(OpcionExamen)
admin.site.register(PreguntaExamen)
