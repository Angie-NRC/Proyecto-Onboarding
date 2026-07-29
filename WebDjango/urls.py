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




]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
