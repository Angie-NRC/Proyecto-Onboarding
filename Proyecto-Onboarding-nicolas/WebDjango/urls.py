from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('usuarios/salir/', views.salir, name='salir'),
    
    path('usuarios/login/', views.login, name='login'),
    
    path('usuarios/registro/', views.registro, name='registro'),
    
    path('home/', views.home, name='home'),
    
    path('', views.login, name='login'),
    
    path('Modulo/Registrar',  views.registro_modulo_y_cursos,  name='registro_modulo_y_cursos'), 
    
    path("unidades/", views.unidadesNRC, name="unidadesNRC"),
    
    path('Modulos/Unidad/<int:unidad_id>/', views.modulosUnidades, name="modulosUnidades"),
    
    path('Modulos/<int:modulo_id>/detalle/',views.cursosVideosModulo,name='cursosVideosModulo'),
    
    path('Cursos/Videos/<int:video_id>', views.videosCursos, name='videosCursos'), 
    
    
    path('Modulos/<int:modulo_id>/cursos/', views.cursosModulos, name='cursosModulos'),

    path('admin/', admin.site.urls),

path('examen/<int:video_id>/', views.examen, name='examen'),

path('examen/resultado/<int:resultado_id>/', views.resultado_examen, name='resultado_examen'),

path('mi-progreso/', views.mi_progreso, name='mi_progreso'),

    # Rutas del Panel de Administración
    path('panel/', views.panel_dashboard, name='panel_dashboard'),
    path('panel/usuarios/', views.panel_usuarios, name='panel_usuarios'),
    path('panel/usuarios/<int:usuario_id>/editar/', views.panel_editar_usuario, name='panel_editar_usuario'),
    path('panel/cuestionarios/', views.panel_cuestionarios, name='panel_cuestionarios'),
    path('panel/cuestionarios/<int:examen_id>/editar/', views.panel_editar_cuestionario, name='panel_editar_cuestionario'),
    path('panel/cuestionarios/crear/', views.panel_crear_cuestionario, name='panel_crear_cuestionario'),
    path('panel/resultados/', views.panel_resultados, name='panel_resultados'),
    path('panel/contenido/', views.panel_contenido, name='panel_contenido'),
    path('panel/contenido/modulo/<int:modulo_id>/editar/', views.panel_editar_modulo, name='panel_editar_modulo'),
    path('panel/contenido/curso/crear/', views.panel_crear_curso, name='panel_crear_curso'),
    path('panel/contenido/curso/<int:curso_id>/editar/', views.panel_editar_curso, name='panel_editar_curso'),
    path('panel/contenido/curso/<int:curso_id>/video/agregar/', views.panel_agregar_video, name='panel_agregar_video'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
