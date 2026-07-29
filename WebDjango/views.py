from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as lg, authenticate, logout
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import Registro,  Modulo_Form
from .models import (
    Curso,
    Unidad,
    Modulo,
    videos,
    Examen,
    ProgresoCurso
)
from django.db import transaction

# Página principal (home)
def home(request):
    return render(request, 'home.html')


# Login de usuarios
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuario = authenticate(username=username, password=password)

        if usuario:
            lg(request, usuario)
            messages.success(request, f'Bienvenido {usuario.username}')
            return redirect('home')  
        else:
            messages.error(request, 'Datos incorrectos')

    return render(request, 'user/login.html')


# Registro de usuarios
def registro(request):
    form = Registro(request.POST or None)

    print("=== ENTRÓ A REGISTRO ===")
    print("METHOD:", request.method)
    print("POST DATA:", request.POST)

    if request.method == 'POST':
        print("ES POST")
        print("FORM VALID?:", form.is_valid())
        print("FORM ERRORS:", form.errors)

        if form.is_valid():
            usuario = form.save()
            lg(request, usuario)
            return redirect('home')

    return render(request, 'user/registro.html', {'form': form})



# Cerrar sesión Usuarios 
@require_POST
def salir(request):
    logout(request)
    return redirect('login')


# Registro de cursos/Modulos/Examenes 

def registro_modulo_y_cursos(request):
    if request.method == 'POST':
        modulo_form = Modulo_Form(request.POST, request.FILES)
        if modulo_form.is_valid():
            try:
                with transaction.atomic():
                    modulo = modulo_form.save()

                    total_cursos = int(request.POST.get('total_cursos', 0))
                    for i in range(total_cursos):
                        nombre_curso = request.POST.get(f'nombreCurso-{i}')
                        if nombre_curso:
                            curso = Curso.objects.create(moduloCurso=modulo, nombreCurso=nombre_curso)

                            # Guardar videos del curso
                            for video in request.FILES.getlist(f"videoSet-{i}[]"):
                                v = videos.objects.create(curso=curso, video=video, nombreVideo=video.name)
                                Examen.objects.create(video=v, tituloExamen=f"Examen {video.name}")

                messages.success(request, "Módulo, cursos y videos registrados correctamente.")
                return redirect('unidadesNRC')
            except Exception as e:
                print("ERROR GENERAL:", str(e))
                messages.error(request, "Ocurrió un error al guardar la información.")
        else:
            print("Errores módulo:", modulo_form.errors)
    else:
        modulo_form = Modulo_Form()

    return render(
        request,
        'registroModulosCursos.html',
        {'modulo': modulo_form}
    )











# SE MIRAN LAS UNIDADES DISPONIBLES 

def unidadesNRC(request):
    unidades = Unidad.objects.all()
    return render(request, "unidadesNrc.html", {
        "unidades": unidades
    })



# SE MIRAN LOS MODULOS POR UNIDADES 
def modulosUnidades(request, unidad_id):
    unidad = get_object_or_404(Unidad, id=unidad_id)
    modulos = Modulo.objects.filter(unidadModulos=unidad) 

    return render(request, 'modulos.html', {
        'unidad': unidad,
        'modulos': modulos
    })



# SE MIRAN LAS  CURSOS POR MODULOS 
def cursosModulos(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    cursos = Curso.objects.filter(moduloCurso=modulo)  
    
    return render(request, 'cursos.html', {
        'modulo': modulo,
        'cursos': cursos
    })





# VIDEOS CURSOS 

def videosCursos(request, video_id):

    videoActual = get_object_or_404(
        videos,
        id=video_id
    )

    curso = videoActual.curso

    listVideos = list(
        curso.videos.order_by("ordenVideos")
    )

    htmlActual = listVideos.index(videoActual)

    video_siguiente = (
        listVideos[htmlActual + 1]
        if htmlActual + 1 < len(listVideos)
        else None
    )

    return render(
        request,
        "videos_Cursos.html",
        {
            "video": videoActual,
            "video_siguiente": video_siguiente,
            "curso": curso
        }
    )   

# SE VEN LOS VIDEOS DE ACUREDO A LOS CURSOS 

def cursosVideosModulo(request, modulo_id):
    modulo = get_object_or_404(
        Modulo.objects.prefetch_related('curso_set__videos_set'),
        id=modulo_id
    )

    return render(request, 'cursos.html', {
        'modulo': modulo
    })



def examen(request, video_id):

    video = get_object_or_404(videos, id=video_id)

    examen = getattr(video, "examen", None)

    return render(request, "examen.html", {
        "video": video,
        "examen": examen
    })


