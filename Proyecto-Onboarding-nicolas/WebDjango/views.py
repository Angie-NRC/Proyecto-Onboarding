from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as lg, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import Registro, Modulo_Form
from .models import (
    Curso,
    Unidad,
    Modulo,
    videos,
    Examen,
    ProgresoCurso,
    ResultadoCuestionario,
    OpcionExamen,
    User as CustomUser,
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

    videoActual = get_object_or_404(videos, id=video_id)
    curso = videoActual.curso
    listVideos = list(curso.videos.order_by("ordenVideos"))
    htmlActual = listVideos.index(videoActual)
    video_siguiente = (
        listVideos[htmlActual + 1]
        if htmlActual + 1 < len(listVideos)
        else None
    )

    # Guardar progreso si el usuario está autenticado
    if request.user.is_authenticated:
        custom_user, _ = CustomUser.objects.get_or_create(
            nombreUser=request.user.username
        )
        ProgresoCurso.objects.update_or_create(
            usuario=custom_user,
            curso=curso,
            defaults={'ultimo_video': videoActual}
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
    examen_obj = getattr(video, "examen", None)

    custom_user = None
    intentos = []
    ya_aprobado = False

    if request.user.is_authenticated and examen_obj:
        custom_user, _ = CustomUser.objects.get_or_create(
            nombreUser=request.user.username
        )
        intentos = list(
            ResultadoCuestionario.objects.filter(
                usuario=custom_user, examen=examen_obj
            ).order_by('-intento')
        )
        ya_aprobado = any(r.aprobado for r in intentos)

    if request.method == 'POST' and examen_obj and custom_user and not ya_aprobado:
        preguntas = examen_obj.preguntas.prefetch_related('opciones').all()
        total = preguntas.count()
        correctas = 0

        for pregunta in preguntas:
            opcion_id = request.POST.get(f'pregunta_{pregunta.id}')
            if opcion_id:
                try:
                    opcion = OpcionExamen.objects.get(id=opcion_id)
                    if opcion.opcionCorrecta:
                        correctas += 1
                except OpcionExamen.DoesNotExist:
                    pass

        puntaje = round((correctas / total) * 100) if total > 0 else 0
        aprobado = puntaje >= 70

        nuevo_intento = (intentos[0].intento + 1) if intentos else 1

        resultado = ResultadoCuestionario.objects.create(
            usuario=custom_user,
            examen=examen_obj,
            puntaje=puntaje,
            aprobado=aprobado,
            intento=nuevo_intento
        )
        return redirect('resultado_examen', resultado_id=resultado.id)

    return render(request, "examen.html", {
        "video": video,
        "examen": examen_obj,
        "intentos": intentos,
        "ya_aprobado": ya_aprobado,
    })

# VISTAS DEL PANEL DE ADMIN
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User as AuthUser
from .models import User as CustomUser, ResultadoCuestionario, PreguntaExamen, OpcionExamen
from .forms import EditarUsuarioForm, EditarPerfilForm, ExamenForm, PreguntaFormSet, OpcionFormSet, EditarCursoForm
from django.core.paginator import Paginator

@staff_member_required
def panel_dashboard(request):
    total_usuarios = AuthUser.objects.count()
    total_modulos = Modulo.objects.count()
    total_examenes = Examen.objects.count()
    ultimos_resultados = ResultadoCuestionario.objects.select_related('usuario', 'examen').order_by('-id')[:5]
    
    return render(request, 'admin_panel/dashboard.html', {
        'total_usuarios': total_usuarios,
        'total_modulos': total_modulos,
        'total_examenes': total_examenes,
        'ultimos_resultados': ultimos_resultados
    })

@staff_member_required
def panel_usuarios(request):
    query = request.GET.get('q', '')
    usuarios_list = AuthUser.objects.all().order_by('-date_joined')
    if query:
        usuarios_list = usuarios_list.filter(username__icontains=query)
        
    paginator = Paginator(usuarios_list, 10)
    page_number = request.GET.get('page')
    usuarios = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/usuarios.html', {'usuarios': usuarios, 'query': query})

@staff_member_required
def panel_editar_usuario(request, usuario_id):
    auth_user = get_object_or_404(AuthUser, id=usuario_id)
    # Get or create CustomUser profile
    custom_user = CustomUser.objects.filter(nombreUser=auth_user.username).first()
    if not custom_user:
        custom_user = CustomUser.objects.create(nombreUser=auth_user.username)
    
    if request.method == 'POST':
        form_auth = EditarUsuarioForm(request.POST, instance=auth_user)
        form_perfil = EditarPerfilForm(request.POST, instance=custom_user)
        
        if form_auth.is_valid() and form_perfil.is_valid():
            form_auth.save()
            form_perfil.save()
            messages.success(request, 'Usuario actualizado correctamente.')
            return redirect('panel_usuarios')
    else:
        form_auth = EditarUsuarioForm(instance=auth_user)
        form_perfil = EditarPerfilForm(instance=custom_user)
        
    return render(request, 'admin_panel/editar_usuario.html', {
        'form_auth': form_auth,
        'form_perfil': form_perfil,
        'usuario': auth_user
    })

@staff_member_required
def panel_cuestionarios(request):
    examenes = Examen.objects.all().order_by('id')
    return render(request, 'admin_panel/cuestionarios.html', {'examenes': examenes})

@staff_member_required
def panel_editar_cuestionario(request, examen_id):
    examen = get_object_or_404(Examen, id=examen_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'guardar_titulo':
            titulo = request.POST.get('tituloExamen')
            if titulo:
                examen.tituloExamen = titulo.strip()
                examen.save()
                messages.success(request, 'Título del examen actualizado.')

        elif action == 'agregar_pregunta':
            texto_pregunta = request.POST.get('textoPregunta')
            opciones_text = [
                request.POST.get('opcion_0'),
                request.POST.get('opcion_1'),
                request.POST.get('opcion_2'),
                request.POST.get('opcion_3'),
            ]
            correcta_idx = request.POST.get('opcion_correcta')  # '0', '1', '2', '3'

            if texto_pregunta and any(t for t in opciones_text if t and t.strip()):
                pregunta = PreguntaExamen.objects.create(
                    examen=examen,
                    textoPregunta=texto_pregunta.strip()
                )
                for idx, opt_text in enumerate(opciones_text):
                    if opt_text and opt_text.strip():
                        is_correct = (str(idx) == str(correcta_idx))
                        OpcionExamen.objects.create(
                            pregunta=pregunta,
                            textoOpcion=opt_text.strip(),
                            opcionCorrecta=is_correct
                        )
                messages.success(request, 'Pregunta y sus opciones registradas correctamente.')
            else:
                messages.error(request, 'Debes ingresar el texto de la pregunta y al menos una opción.')

        elif action == 'eliminar_pregunta':
            pregunta_id = request.POST.get('pregunta_id')
            if pregunta_id:
                PreguntaExamen.objects.filter(id=pregunta_id, examen=examen).delete()
                messages.success(request, 'Pregunta eliminada.')

        return redirect('panel_editar_cuestionario', examen_id=examen.id)

    preguntas = examen.preguntas.prefetch_related('opciones').all()
    return render(request, 'admin_panel/editar_cuestionario.html', {
        'examen': examen,
        'preguntas': preguntas
    })

@staff_member_required
def panel_crear_cuestionario(request):
    if request.method == 'POST':
        form = ExamenForm(request.POST)
        if form.is_valid():
            examen = form.save()
            messages.success(request, 'Examen creado. Ahora añade las preguntas.')
            return redirect('panel_editar_cuestionario', examen_id=examen.id)
    else:
        form = ExamenForm()
    return render(request, 'admin_panel/crear_cuestionario.html', {'form': form})

@staff_member_required
def panel_resultados(request):
    resultados = ResultadoCuestionario.objects.select_related('usuario', 'examen').order_by('-id')
    paginator = Paginator(resultados, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'admin_panel/resultados.html', {'resultados': page_obj})

@staff_member_required
def panel_contenido(request):
    modulos = Modulo.objects.prefetch_related('curso_set').all()
    return render(request, 'admin_panel/contenido.html', {'modulos': modulos})

@staff_member_required
def panel_editar_modulo(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    if request.method == 'POST':
        form = Modulo_Form(request.POST, request.FILES, instance=modulo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Módulo actualizado.')
            return redirect('panel_contenido')
    else:
        form = Modulo_Form(instance=modulo)
    return render(request, 'admin_panel/editar_modulo.html', {'form': form, 'modulo': modulo})

@staff_member_required
def panel_editar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        form = EditarCursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            
            # Subir nuevo video si se envió alguno desde esta pantalla
            archivos_video = request.FILES.getlist('nuevos_videos')
            for archivo in archivos_video:
                v = videos.objects.create(curso=curso, video=archivo, nombreVideo=archivo.name)
                Examen.objects.create(video=v, tituloExamen=f"Examen - {archivo.name}")
                
            messages.success(request, 'Curso y videos actualizados correctamente.')
            return redirect('panel_contenido')
    else:
        form = EditarCursoForm(instance=curso)
    return render(request, 'admin_panel/editar_curso.html', {'form': form, 'curso': curso})

@staff_member_required
def panel_crear_curso(request):
    modulo_id = request.GET.get('modulo_id')
    modulo_inicial = None
    if modulo_id:
        modulo_inicial = get_object_or_404(Modulo, id=modulo_id)

    if request.method == 'POST':
        form = EditarCursoForm(request.POST)
        if form.is_valid():
            curso = form.save()
            
            # Subir videos adjuntos y crear sus cuestionarios automáticamente
            archivos_video = request.FILES.getlist('videos')
            for archivo in archivos_video:
                v = videos.objects.create(curso=curso, video=archivo, nombreVideo=archivo.name)
                Examen.objects.create(video=v, tituloExamen=f"Examen - {archivo.name}")

            messages.success(request, f'Curso "{curso.nombreCurso}" y sus videos agregados correctamente.')
            return redirect('panel_contenido')
    else:
        initial = {'moduloCurso': modulo_inicial} if modulo_inicial else {}
        form = EditarCursoForm(initial=initial)

    return render(request, 'admin_panel/crear_curso.html', {'form': form, 'modulo_inicial': modulo_inicial})

@staff_member_required
def panel_agregar_video(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        nombre_video = request.POST.get('nombreVideo')
        archivo_video = request.FILES.get('video')
        if archivo_video:
            nombre = nombre_video.strip() if nombre_video and nombre_video.strip() else archivo_video.name
            v = videos.objects.create(curso=curso, video=archivo_video, nombreVideo=nombre)
            examen_obj = Examen.objects.create(video=v, tituloExamen=f"Examen - {nombre}")
            messages.success(request, f'Video "{nombre}" subido correctamente. Ahora configura las preguntas de su cuestionario.')
            return redirect('panel_editar_cuestionario', examen_id=examen_obj.id)
        else:
            messages.error(request, 'Debes seleccionar un archivo de video.')
    return render(request, 'admin_panel/agregar_video.html', {'curso': curso})


# ==================== SISTEMA DE EVALUACIÓN ====================

def resultado_examen(request, resultado_id):
    resultado = get_object_or_404(ResultadoCuestionario, id=resultado_id)

    # Verificar que el resultado pertenece al usuario actual
    if request.user.is_authenticated:
        custom_user, _ = CustomUser.objects.get_or_create(
            nombreUser=request.user.username
        )
        if resultado.usuario != custom_user:
            return redirect('home')
    else:
        return redirect('login')

    examen_obj = resultado.examen
    video = examen_obj.video

    # Obtener todos los intentos para mostrar historial
    todos_intentos = ResultadoCuestionario.objects.filter(
        usuario=resultado.usuario,
        examen=examen_obj
    ).order_by('intento')

    return render(request, "resultado_examen.html", {
        "resultado": resultado,
        "examen": examen_obj,
        "video": video,
        "todos_intentos": todos_intentos,
    })


@login_required
def mi_progreso(request):
    custom_user, _ = CustomUser.objects.get_or_create(
        nombreUser=request.user.username
    )

    modulos = Modulo.objects.prefetch_related('curso_set__videos').all()
    progreso_data = []

    for modulo in modulos:
        cursos_data = []
        total_videos_modulo = 0
        videos_vistos_modulo = 0

        for curso in modulo.curso_set.all():
            videos_ordenados = list(curso.videos.order_by('ordenVideos'))
            total_videos = len(videos_ordenados)

            # Calcular videos vistos
            videos_vistos = 0
            ultimo_video = None
            try:
                progreso = ProgresoCurso.objects.get(
                    usuario=custom_user, curso=curso
                )
                ultimo_video = progreso.ultimo_video
                if ultimo_video in videos_ordenados:
                    videos_vistos = videos_ordenados.index(ultimo_video) + 1
            except ProgresoCurso.DoesNotExist:
                pass

            # Obtener todos los intentos del examen de este curso
            intentos_curso = ResultadoCuestionario.objects.filter(
                usuario=custom_user,
                examen__video__curso=curso
            ).order_by('-intento')

            mejor_resultado = None
            if intentos_curso.exists():
                aprobados = intentos_curso.filter(aprobado=True)
                mejor_resultado = aprobados.first() if aprobados.exists() else intentos_curso.first()

            # Obtener primer video del curso para el botón de inicio
            primer_video = videos_ordenados[0] if videos_ordenados else None

            porcentaje_curso = round(
                (videos_vistos / total_videos) * 100
            ) if total_videos > 0 else 0

            total_videos_modulo += total_videos
            videos_vistos_modulo += videos_vistos

            cursos_data.append({
                'curso': curso,
                'total_videos': total_videos,
                'videos_vistos': videos_vistos,
                'porcentaje': porcentaje_curso,
                'mejor_resultado': mejor_resultado,
                'total_intentos': intentos_curso.count(),
                'lista_intentos': list(intentos_curso),
                'primer_video': primer_video,
                'ultimo_video': ultimo_video,
            })

        porcentaje_modulo = round(
            (videos_vistos_modulo / total_videos_modulo) * 100
        ) if total_videos_modulo > 0 else 0

        progreso_data.append({
            'modulo': modulo,
            'cursos': cursos_data,
            'porcentaje': porcentaje_modulo,
        })

    return render(request, "mi_progreso.html", {
        "progreso_data": progreso_data,
        "custom_user": custom_user,
    })
