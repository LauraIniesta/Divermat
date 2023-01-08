from contextlib import nullcontext
from http.client import HTTPException
from django.shortcuts import render, redirect

from divermat.models import (Profesor, Alumno, Usuario, User,
                    Clase, Curso, Ejercicio,Seguimiento,
                    Examen, Video, Resumen,Tema)

from divermat.forms import NuevoAlumno, NuevoExamen, Registro, NuevaClase, NuevaInfoProfesor,NuevaInfoAlumno, NuevaInfoClase,InicioSesion
from django.contrib.auth.forms import PasswordChangeForm
from django.core.checks.security import csrf
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from strgen import StringGenerator
from unidecode import unidecode


def index(request):
    content = {}
    content['registro'] = False
    content['Tipo'] = 'Ejercicios'
    content['Contenido'] = {}
    todos_ejs = Ejercicio.objects.all()
    ejercicios = []
    for elem in todos_ejs:
        ejercicio = {}
        ejercicio['id'] = elem.id
        ejercicio['titulo'] = elem.titulo
        ejercicios.append(ejercicio)
    content['Contenido'] = ejercicios
    temas = []
    for tema in Tema.objects.all():
        temas.append(tema.titulo)
    content['temas'] = temas

    busqueda = request.GET.get('buscar', '')
    curso = request.GET.get('curso', '')
    tema = request.GET.get('tema', '')
    tipo = request.GET.get('tipo', '')

    ejercicios = []
    if busqueda and busqueda != "Buscar":
        
        for elem in todos_ejs:
            if unidecode(busqueda.lower()) in unidecode(elem.titulo.lower()):
                ejercicio = {}
                ejercicio['id'] = elem.id
                ejercicio['titulo'] = elem.titulo
                if ejercicio not in ejercicios:
                    ejercicios.append(ejercicio)
        content['Contenido'] = ejercicios

    if curso and curso != "Curso":
        for elem in todos_ejs:
            if curso == elem.curso:
                ejercicio = {}
                ejercicio['id'] = elem.id
                ejercicio['titulo'] = elem.titulo
                if ejercicio not in ejercicios:
                    ejercicios.append(ejercicio)
        content['Contenido'] = ejercicios

    if tema and tema != "Tema":
        for elem in todos_ejs:
            if str(tema) in str(elem.tema):
                ejercicio = {}
                ejercicio['id'] = elem.id
                ejercicio['titulo'] = elem.titulo
                if ejercicio not in ejercicios:
                    ejercicios.append(ejercicio)
        content['Contenido'] = ejercicios
    if tipo and tipo != "Tipo":
        if tipo == "Test":
            tipos = 1
        elif tipo == "Respuesta corta":
            tipos = 2
        else:
            tipos = 3
        for elem in todos_ejs:
            if tipos == elem.tipo:
                ejercicio = {}
                ejercicio['id'] = elem.id
                ejercicio['titulo'] = elem.titulo
                if ejercicio not in ejercicios:    
                    ejercicios.append(ejercicio)
        content['Contenido'] = ejercicios

    if request.user.is_authenticated:
    
        try:
            content['tipo'] = "Profesor"
            profesor = Profesor.objects.get(username=request.user)
            clases = Clase.objects.filter(profesor=profesor)
            content['clases'] = clases
            lista = request.POST.getlist("Ejercicios")
            clase_sel = request.POST.get("Clase",'')
            clase = None
            for c in clases:
                if str(c) == clase_sel:
                    clase = c
                    break
            if request.method == 'POST':
                if lista and clase:
                    for id in lista:
                        ejercicio = Ejercicio.objects.get(id=id)
                        clase.ejercicios.add(ejercicio)
                    clase.save()
            return render(request,'divermat/ejerciciosprof.html', context=content)

        except Profesor.DoesNotExist:
  ###
            try:
                alumno = Alumno.objects.get(username=request.user)
                content['clases'] = alumno.clase
                ejercicios_alumno = []
                for elem in ejercicios:
                    if elem.curso == alumno.curso:
                        ejercicio = {}
                        ejercicio['id'] = elem.id
                        ejercicio['titulo'] = elem.titulo
                        ejercicios_alumno.append(ejercicio)
                content['Contenido'] = ejercicios_alumno
            except Alumno.DoesNotExist:
                alumno = None
    
        content['usuario'] = request.user.username
        
                #Si así no funciona hay que hacer en el model de ejercicios un OneToMany field que apunte a ejercicios y para saber quien lo ha hecho
                #Podría hacer otro OneToMany en Alumno y recorrer aquí quien los ha hecho
                #Eso o crear un modelo que sea seguimientoClase e indique una ref al ejercicio, un valor de acierto y num hechos q se actualicen cada vez que un alumno
                #Haga un ejercicio

    return render(request,'divermat/inicio.html', context=content,)


class registro(CreateView):
    model = Profesor
    form_class = Registro
    template_name = 'divermat/registro.html'

    def form_valid(self, form):
        
        form.save()
        nusuario = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        usuario = authenticate(username=nusuario, password=password)
        login(self.request, usuario)
        return redirect('/')


def iniciar_sesion(request):
    content = {}
    if request.method == 'POST':
        form = InicioSesion(request.POST)

        if form.is_valid():

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            try:
                alumno = Alumno.objects.get(username=username)
                if alumno.password_temporal == password:
                    usuario = authenticate(username=username, password=password)
                    login(request, usuario)
                    return redirect('cambiar_contrasenia')
            except Alumno.DoesNotExist:
                alumno = None
                content['error'] = "El usuario de tipo Alumno con ese nombre de usuario no existe."              
            
            usuario = authenticate(username=username, password=password)
            login(request, usuario)
            return redirect('/')

    content['form'] = InicioSesion()
    return render(request,'divermat/inicio_sesion.html', context=content,)

class cerrar_sesion(LogoutView):
    pass

@login_required
def perfil(request):

    try:
        usuario = Profesor.objects.get(username=request.user)
        return perfilProfesor(request,usuario)
    except Profesor.DoesNotExist:
        try:
            usuario = Alumno.objects.get(username=request.user)
            return perfilAlumno(request,usuario)
        except Alumno.DoesNotExist:
            return redirect('/')

@login_required
def perfilProfesor(request,profesor):
    #Opcion de cambiar contraseña username o centro anñadr
    content = {}
    content['registro'] = False

    if request.method == 'POST':
        form = NuevaInfoProfesor(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            centro = form.cleaned_data['centro']
            if username != "":
                profesor.username = username
                profesor.save()
            if centro != "":
                profesor.centro = centro
                profesor.save() 
    content['form'] = NuevaInfoProfesor()

    content['nombre'] = profesor.first_name 
    content['apellidos'] = profesor.last_name
    content['username'] = profesor.username
    content['centro'] = profesor.centro
    content['alumno'] = False
    
    return render(request,'divermat/perfil.html', context=content,)

@login_required
def perfilAlumno(request,alumno):
    content = {}
    content['registro'] = False

    if request.method == 'POST':
        form = NuevaInfoAlumno(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            if first_name != "":
                alumno.first_name = first_name
                alumno.save()
            if last_name != "":
                alumno.last_name = last_name
                alumno.save()
    content['form'] = NuevaInfoAlumno()

    content['nombre'] = alumno.first_name 
    content['apellidos'] = alumno.last_name
    content['username'] = alumno.username
    content['centro'] = alumno.centro
    content['alumno'] = True
    content['clase'] = alumno.clase
    #Para que se vea que funciona el seguimiento
    # segui = Seguimiento()
    # segui.alumno = alumno
    # segui.acierto=1
    # segui.n_ejercicios=0
    # segui.save()
    content['seguimiento'] = Seguimiento.objects.filter(alumno=alumno)
    
    return render(request,'divermat/perfil.html', context=content,)

@login_required
def cambiarInformacionAlumno(request):
    content = {}
    content['registro'] = False
    try:
        alumno = Alumno.objects.get(username=request.user)
        if request.method == 'POST':
            form = NuevaInfoAlumno(request.POST)
            if form.is_valid():
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                if first_name != "":
                    alumno.first_name = first_name
                    alumno.save()
                if last_name != "":
                    alumno.last_name = last_name
                    alumno.save()
        content['form'] = NuevaInfoAlumno()

        content['nombre'] = alumno.first_name 
        content['apellidos'] = alumno.last_name
        content['username'] = alumno.username
        content['centro'] = alumno.centro
        
        return render(request,'divermat/cambiarInformacionAlumno.html', context=content,)

    except Alumno.DoesNotExist:
        return redirect('/')

class PasswordChangeView(PasswordChangeView):
    template_name = 'divermat/cambiocontrasenia.html' # El tamplate_name por defecto es: 'registration/password_change_form.html'
    form_class = PasswordChangeForm
    success_url = 'divermat/perfil.html' 


def examenes(request):
    content = {}
    content['registro'] = False
    if request.user.is_authenticated:
        if request.user.tipo == 2:
            try:
                usuario = Alumno.objects.get(username=request.user.username)
            except Alumno.DoesNotExist:
                usuario = None

        content = {}
        content['registro'] = False
        content['examen'] = False

        if request.method == 'POST':
            form = NuevoExamen(request.POST)
            if form.is_valid():

                #Crear un examen que tenga 10 preguntas del tema y curso seleccionado y mostrarlo
                temas = form.cleaned_data['temas']
                curso = form.cleaned_data['curso'] 
                #crono = form.cleaned_data['crono']

                if usuario:
                    usuario.numexamen += 1
                    nExamen = usuario.numexamen
                    content['examen'] = True
                    content['n_examen'] = nExamen
            else:
                content['error'] = "Error en el formulario"
        
        else:
            #Usuario iniciada sesion y quiere rellenar el formulario
            if usuario is None:
                c = None
            else:
                c = usuario.curso
            form = NuevoExamen(curso=c)
            
            content['form'] = form
    else:
        if request.method == 'POST':
            form = NuevoExamen(request.POST)

            if form.is_valid():

                #Crear un examen que tenga 10 preguntas del tema y curso seleccionado y mostrarlo
                temas = form.cleaned_data['temas']
                curso = form.cleaned_data['curso'] 
                #crono = form.cleaned_data['crono']

                content['examen'] = True
                content['n_examen'] = 1
            else:
                content['error'] = "Error en el formulario"
        
        else:
            #Usuario no iniciada sesion y quiere rellenar el formulario
            form = NuevoExamen(None)
            content['form'] = form  

    return render(request,'divermat/examenes.html', context=content,)


def videos(request):
    #Mostrar en pequeño la ventana del video
    content = {}
    content['registro'] = False
    content['Tipo'] = 'Videos'
    content['Contenido'] = {}
    todos_videos = Video.objects.all()
    videos = []
    for elem in todos_videos:
        video = {}
        video['id'] = elem.id
        video['titulo'] = elem.titulo
        videos.append(video)
    content['Contenido'] = videos
    temas = []
    for tema in Tema.objects.all():
        temas.append(tema.titulo)
    content['temas'] = temas

    busqueda = request.GET.get('buscar', '')
    curso = request.GET.get('curso', '')
    tema = request.GET.get('tema', '')
    tipo = request.GET.get('tipo', '')

    ejercicios = []
    if busqueda and busqueda != "Buscar":
        
        for elem in todos_videos:
            if unidecode(busqueda.lower()) in unidecode(elem.titulo.lower()):
                video = {}
                video['id'] = elem.id
                video['titulo'] = elem.titulo
                videos.append(video)
        content['Contenido'] = videos

    if curso and curso != "Curso":
        for elem in todos_videos:
            if curso == elem.curso:
                video = {}
                video['id'] = elem.id
                video['titulo'] = elem.titulo
                if video not in videos:
                    videos.append(video)
        content['Contenido'] = videos

    if tema and tema != "Tema":
        for elem in todos_videos:
            if str(tema) in str(elem.tema):
                video = {}
                video['id'] = elem.id
                video['titulo'] = elem.titulo
                if video not in videos:
                    videos.append(video)
        content['Contenido'] = videos

    if tipo and tipo != "Tipo":
        if tipo == "Test":
            tipos = 1
        elif tipo == "Respuesta corta":
            tipos = 2
        else:
            tipos = 3
        for elem in todos_videos:
            if tipos == elem.tipo:
                video = {}
                video['id'] = elem.id
                video['titulo'] = elem.titulo
                if video not in videos:
                    videos.append(video)
        content['Contenido'] = videos


    return render(request,'divermat/inicio.html', context=content,)


#Mostrar el video como tal para obtener respuesta del usuario
def video(request):

    return render(request,'divermat/video.html', )


def resumenes(request):

    content = {}
    content['registro'] = False
    content['Tipo'] = 'Resúmenes'
    content['Contenido'] = {}
    todos_res = Resumen.objects.all()
    resumenes = []
    for elem in todos_res:
        resumen = {}
        resumen['id'] = elem.id
        resumen['titulo'] = elem.titulo
        resumenes.append(resumen)
    content['Contenido'] = resumenes
    temas = []
    for tema in Tema.objects.all():
        temas.append(tema.titulo)
    content['temas'] = temas

    busqueda = request.GET.get('buscar', '')
    curso = request.GET.get('curso', '')
    tema = request.GET.get('tema', '')
    tipo = request.GET.get('tipo', '')

    resumenes = []
    if busqueda and busqueda != "Buscar":
        
        for elem in todos_res:
            if unidecode(busqueda.lower()) in unidecode(elem.titulo.lower()):
                resumen = {}
                resumen['id'] = elem.id
                resumen['titulo'] = elem.titulo
                resumenes.append(resumen)
        content['Contenido'] = resumenes

    if curso and curso != "Curso":
        for elem in todos_res:
            if curso == elem.curso:
                resumen = {}
                resumen['id'] = elem.id
                resumen['titulo'] = elem.titulo
                if resumen not in resumenes:
                    resumenes.append(resumen)
        content['Contenido'] = resumenes

    if tema and tema != "Tema":
        for elem in todos_res:
            if str(tema) in str(elem.tema):
                resumen = {}
                resumen['id'] = elem.id
                resumen['titulo'] = elem.titulo
                if resumen not in resumenes:
                    resumenes.append(resumen)
        content['Contenido'] = resumenes

    if tipo and tipo != "Tipo":
        if tipo == "Test":
            tipos = 1
        elif tipo == "Respuesta corta":
            tipos = 2
        else:
            tipos = 3
        for elem in todos_res:
            if tipos == elem.tipo:
                resumen = {}
                resumen['id'] = elem.id
                resumen['titulo'] = elem.titulo
                if resumen not in resumenes:
                    resumenes.append(resumen)
        content['Contenido'] = resumenes
    
    return render(request,'divermat/inicio.html', context=content,)


#Mostrar el resumen como tal para obtener respuesta del usuario
def resumen(request):

    return render(request,'divermat/resumen.html', )


#Mostrar el ejercicio como tal para obtener respuesta del usuario
def ejercicio(request):

    return render(request,'divermat/ejercicio.html', )


@login_required
def clases(request):

    content = {}
    content['registro'] = False
    profesor = Profesor.objects.get(username=request.user)
    clasesProf = Clase.objects.filter(profesor=profesor)

    busqueda = request.GET.get('buscar', '')
    filtro = request.GET.get('curso', '')
    content['clases'] = []
    clases = []
    if busqueda and busqueda != "Buscar Clase":
        for c in clasesProf:
            if unidecode(busqueda.lower()) in unidecode(c.nombre.lower()) or unidecode(busqueda.lower()) in unidecode(str(c.centro).lower()):
                clases.append(c)
            elif unidecode(busqueda.lower()) in unidecode(str(c.curso).lower()) or unidecode(busqueda.lower()) in unidecode(str(c.ano_academico).lower()):
                clases.append(c)
    else:
        clases = clasesProf
    
    if filtro and filtro != "Curso":
        for c in clases:
            if str(c.curso)+"º ESO" == filtro:
                content['clases'].append(c)
    else:
        content['clases'] = clases

    if request.method == 'POST':
        form = NuevaClase(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            curso = form.cleaned_data['curso']
            n_alumnos = form.cleaned_data['n_alumnos']
           # alumnos_auto = form.cleaned_data['alumnos_auto']
            ano_academico = form.cleaned_data['ano_academico']
            clase = Clase()
            clase.nombre = nombre
            clase.curso = curso
            clase.ano_academico = ano_academico
            clase.n_alumnos = n_alumnos
            clase.centro = profesor.centro
            clase.profesor = profesor
            clase.save()
            #if alumnos_auto == 'Si':
            alumnos = Alumno.objects.all()
            nalm = len(alumnos)
            # for alm in alumnos:
            #     nalm +=1
            for i in range(0,n_alumnos):
                alumno = Alumno()
                alumno.username = "user_" + str(i+nalm)
                alumno.password = StringGenerator("[\l\d]{10}").render_list(1,unique=True)[0]
                alumno.password_temporal = alumno.password
                alumno.set_password(alumno.password)
                print(alumno.password_temporal)
                alumno.centro = profesor.centro
                alumno.curso = curso
                alumno.clase = clase
                alumno.numexamen = 0
                alumno.tipo = "Alumno"
                alumno.save()
        
    form = NuevaClase(None,None)
    content['form'] = form
    request.method = 'GET'
    return render(request,'divermat/clases.html', context=content,)


@login_required
def alumnos(request, alumno=None):
    busqueda = request.GET.get('buscar', '')
    filtro = request.GET.get('curso', '')
    content = {}
    content['registro'] = False
    content['alumnos'] = []
    alumnos = []
    if busqueda and busqueda != "Buscar Alumno":
        for a in Alumno.objects.all():
            if unidecode(busqueda.lower()) in unidecode(a.first_name.lower()) or unidecode(busqueda.lower()) in unidecode(a.last_name.lower()):
                alumnos.append(a)            
            elif unidecode(busqueda.lower()) in unidecode(a.username.lower()) or unidecode(busqueda.lower()) in unidecode(a.centro.lower()):  
                alumnos.append(a)
    else:
        alumnos = Alumno.objects.all()
    
    if filtro and filtro != "Curso":
        for a in alumnos:
            if str(a.curso)+"º ESO" == filtro:
                content['alumnos'].append(a)
    else:
        content['alumnos'] = alumnos

    if alumno:
        for alum in Alumno.objects.all():
            if alum.id == int(alumno):
                content['alumno'] = alum
                break
        content['informacion'] = Seguimiento.objects.filter(alumno=alum)
        
    return render(request,'divermat/alumnos.html', context=content,)


def contenido(request):
    content = {}
    content['registro'] = False
    content['videos'] = Video.objects.all()
    content['resumenes'] = Resumen.objects.all()
    temas = []
    for tema in Tema.objects.all():
        temas.append(tema.titulo)
    content['temas'] = temas

    todos_videos = Video.objects.all()
    todos_res = Resumen.objects.all()

    busqueda = request.GET.get('buscar', '')
    curso = request.GET.get('curso', '')
    tema = request.GET.get('tema', '')
    tipo = request.GET.get('tipo', '')

    videos = []
    resumenes = []
    if busqueda and busqueda != "Buscar":
        
        for elem in todos_videos:
            if unidecode(busqueda.lower()) in unidecode(elem.titulo.lower()):
                video = {}
                video['id'] = elem.id
                video['titulo'] = elem.titulo
                videos.append(video)

        for elem in todos_res:
            if busqueda in elem.titulo:
                res = {}
                res['id'] = elem.id
                res['titulo'] = elem.titulo
                resumenes.append(res)

        content['videos'] = videos 
        content['resumenes'] = resumenes

    if curso and curso != "Curso":
        for elem in todos_videos:
            if curso == elem.curso:
                video = {}
                video['id'] = elem.id
                video['titulo'] = elem.titulo
                if video not in videos:
                    videos.append(video)
        for elem in todos_res:
            if curso == elem.curso:
                res = {}
                res['id'] = elem.id
                res['titulo'] = elem.titulo
                if res not in resumenes:
                    resumenes.append(res)

        content['videos'] = videos 
        content['resumenes'] = resumenes

    if tema and tema != "Tema":
        for elem in todos_videos:
            if str(tema) in str(elem.tema):
                video = {}
                video['id'] = elem.id
                video['titulo'] = elem.titulo
                if video not in videos:
                    videos.append(video)
        for elem in todos_res:
            if str(tema) in str(elem.tema):
                res = {}
                res['id'] = elem.id
                res['titulo'] = elem.titulo
                if res not in resumenes:
                    resumenes.append(res)

        content['videos'] = videos 
        content['resumenes'] = resumenes

    return render(request,'divermat/contenido.html', context=content,)


@login_required
def clase(request,clase=None):

    content = {}
    content['registro'] = False

    if clase:
        
        flag = False
        for c in Clase.objects.all():
            if c.id == int(clase):
                flag = True
                break
        if flag:
            try:
                usuario = Profesor.objects.get(username=request.user)
                return claseProfesor(request,c)
            except Profesor.DoesNotExist:
                try:
                    usuario = Alumno.objects.get(username=request.user)
                    return claseAlumno(request,c)
                except Alumno.DoesNotExist:
                    return render(request,'divermat/clase.html', context=content,)


@login_required
def claseProfesor(request,clase):
    content = {}
    content['registro'] = False
    content['clase'] = clase
    content['curso'] = clase.curso
    content['ano_academico'] = clase.ano_academico
    content['nombre'] = clase.nombre
    content['nalumnos'] = clase.n_alumnos
    content['centro'] = clase.centro

    alumnos = getAlumnosClase(int(clase.id))

    content['alumnos'] = alumnos
    print(alumnos)
    #Esto hay que comprobarlo cuando seguimiento tenga info en alumnos 
    informacion = []
    for t in Tema.objects.filter(curso=clase.curso):
        infor = {}
        infor['tema'] = str(t.tema) + " " + t.titulo
        acierto = 0
        for alumno in alumnos:
            for segui in Seguimiento.objects.filter(alumno=alumno):
                if segui['tema'] == t:
                    acierto += segui['acierto']
                    break
        infor['acierto'] = acierto/clase.n_alumnos
        informacion.append(infor)
    content['informacion'] = informacion

    return render(request,'divermat/clase.html', context=content,)

def claseAlumno(request,clase=None):
    content = {}
    content['registro'] = False
    #Para probar que salen los ejercicios asignados
    # ej = Ejercicio()
    # ej.titulo = "EJERCICIO PRUEBA"
    # ej.enunciado = ""
    # ej.soluciones = ""
    # ej.save()
    # clase.ejercicios.add(ej)
    # clase.save()
    content['clase'] = clase
    content['curso'] = clase.curso
    content['ano_academico'] = clase.ano_academico
    content['nombre'] = clase.nombre
    content['nalumnos'] = clase.n_alumnos
    content['centro'] = clase.centro
    content['ejercicios'] = clase.ejercicios

    return render(request,'divermat/clase.html', context=content,)

def infoclase(request, claseid=None):
    content={}
    content['registro'] = False

    if claseid:
        for c in Clase.objects.all():
            if c.id == int(claseid):
                flag = True
                break

        if flag:  

            content['clase'] = c
            content['curso'] = c.curso
            content['ano_academico'] = c.ano_academico
            content['nombre'] = c.nombre
            content['centro'] = c.centro

            if request.method == 'POST':
                form = NuevaInfoClase(request.POST)

                if form.is_valid():
                    curso = form.cleaned_data['curso']
                    ano_academico = form.cleaned_data['ano_academico']
                    nombre = form.cleaned_data['nombre']
                    centro = form.cleaned_data['centro']
                    if curso != "":
                        c.curso = curso
                        c.save()
                    if ano_academico != None:
                        c.ano_academico = ano_academico
                        c.save()
                    if nombre != "":
                        c.nombre = nombre
                        c.save()
                    if centro != "":
                        c.centro = centro
                        c.save()

                    return clase(request,claseid)
        
    content['form'] = NuevaInfoClase()
    
    return render(request,'divermat/nuevainfoclase.html', context=content,)


def alumnosclase(request, claseid=None):
    content={}
    content['registro'] = False

    if claseid:
        for c in Clase.objects.all():
            if c.id == int(claseid):
                flag = True
                break

        if flag:  

            alumnos = getAlumnosClase(c.id)
            content['clase'] = c
            content['alumnos'] = alumnos
    if request.method == 'POST':
        lista = request.POST.getlist("Alumnos")
        print(lista)
        for alum in lista:
            alumnoid = alum
            alumno = Alumno.objects.get(id=alumnoid)
            Alumno.objects.filter(id=alumnoid).update(clase=None)
            alumnos = getAlumnosClase(claseid)
            #La lista sale actualizada al haber puesto clase a None en el alumno
            #Clase.objects.filter(id=claseid).update(alumnos=alumnos)
            
            content['clase'] = alumno.clase
            content['alumnos'] = alumnos
        
        form = NuevoAlumno(request.POST)
        
        if form.is_valid():
            n_alumnos = form.cleaned_data['n_alumnos']
            clase = Clase.objects.get(id=claseid)
            content['clase'] = clase
           # alumnos_auto = form.cleaned_data['alumnos_auto']

            #if alumnos_auto == 'Si':
            alumnos = Alumno.objects.all()
            nalm = 0
            for alm in alumnos:
                nalm +=1
            for i in range(0,n_alumnos):
                alumno = Alumno()
                alumno.username = "user_" + str(i+nalm)
                alumno.password = StringGenerator("[\l\d]{10}").render_list(1,unique=True)[0]
                alumno.password_temporal = alumno.password
                alumno.set_password(alumno.password)
                alumno.centro = clase.centro
                alumno.curso = clase.curso
                alumno.clase = clase
                alumno.numexamen = 0
                alumno.tipo = "Alumno"
                alumno.save()
        
    form = NuevoAlumno(None,None)
    content['form'] = form
    
    return render(request,'divermat/alumnosclase.html', context=content,)


def seguimientoclase(request, claseid=None):
    content={}
    content['registro'] = False

    if claseid:
        for c in Clase.objects.all():
            if c.id == int(claseid):
                flag = True
                break

        if flag:  
            alumnos = getAlumnosClase(c.id)
            informacion = []
            for t in Tema.objects.filter(curso=c.curso):
                infor = {}
                infor['tema'] = str(t.tema) + " " + t.titulo
                acierto = 0
                n_ejercicios = 0
                for alumno in alumnos:
                    for segui in Seguimiento.objects.filter(alumno=alumno):
                        if segui['tema'] == t:
                            acierto += segui['acierto']
                            n_ejercicios += segui['ejercicios']
                            break
                infor['acierto'] = acierto/c.n_alumnos
                infor['ejercicios'] = n_ejercicios
                informacion.append(infor)
            content['informacion'] = informacion
            #Comprobarlo cuando estén los alumnos listos
            content['ejercicios_asignados'] = c.ejercicios

    return render(request,'divermat/seguimientoclase.html', context=content,)


def getAlumnosClase(claseid):

    clase = Clase.objects.filter(id=claseid)[0]
    alumnos = Alumno.objects.filter(clase=clase)
    return alumnos



