from contextlib import nullcontext
from http.client import HTTPException
from django.http import Http404
from django.shortcuts import render, redirect

from divermat.models import (Profesor, Alumno, Usuario, User,
                    Clase, Curso, Ejercicio,Seguimiento,
                    Examen, Video, Resumen,Tema,EjercicioUsuario)

from divermat.forms import (NuevoAlumno, NuevoExamen, Registro,
                             NuevaClase, NuevaInfoProfesor,NuevaInfoAlumno,
                             NuevaInfoClase,NuevoSetEjercicios, InicioSesion)

from django.contrib.auth.forms import PasswordChangeForm
from django.core.checks.security import csrf
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from strgen import StringGenerator
from unidecode import unidecode
import random


def index(request):
    content = {}
    content['registro'] = False
    content['Tipo'] = 'Ejercicios'
    content['alumno'] = False
    content['ejercicios'] = True
    todos_ejs = Ejercicio.objects.all()
        
    temas = []
    for tema in Tema.objects.all():
        temas.append(tema.titulo)
    content['temas'] = temas
    
    if request.user.is_authenticated:
        content['usuario'] = request.user.username
        try:
            alumno = Alumno.objects.get(username=request.user)
            content['alumno'] = True
            content['profesor'] = False

            todos_ejs = Ejercicio.objects.filter(curso=alumno.curso)
            temas = []
            for tema in Tema.objects.filter(curso=alumno.curso):
                temas.append(tema.titulo)
            content['temas'] = temas

            if request.method == 'POST':
                
                form = NuevoSetEjercicios(request.POST)
                if form.is_valid():
                    #Crear un examen que tenga 10 preguntas del tema y curso seleccionado y mostrarlo
                    tema = form.cleaned_data['tema']
                    request.method = 'GET'
                    return setEjercicios(request,tema.id)
                else:
                    content['error'] = "Error en el formulario"
            else:
                content['form'] = NuevoSetEjercicios(curso=alumno.curso)
        
            
        except Alumno.DoesNotExist:

            try:
                profesor = Profesor.objects.get(username=request.user)
                content['profesor'] = True
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

                content['Contenido'] = getFilteredContent(todos_ejs,request)
                return render(request,'divermat/ejerciciosprof.html', context=content)

            except Profesor.DoesNotExist:
                profesor = None
    content['Contenido'] = getFilteredContent(todos_ejs,request)

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
    error=False
    if request.method == 'POST':
        form = InicioSesion(request.POST)

        if form.is_valid():

            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            try:
                alumno = Alumno.objects.get(username=username)
                usuario = authenticate(username=username, password=password)
                if usuario:
                    
                    if alumno.password_temporal == password:
                        login(request, usuario)
                        return redirect('cambiar_contrasenia')
                    else:
                        usuario.password_temporal = None
                        usuario.save()
                        login(request, usuario)
                        return redirect('/')
                else:
                    content['error']="Usuario o contraseña incorrectos"
                    error = True

            except Alumno.DoesNotExist:
                alumno = None      
            
            usuario = authenticate(username=username, password=password)
            if usuario:
                login(request, usuario)
                return redirect('/')
            else:
                content['error']="Usuario o contraseña incorrectos"
                error = True

    if error is True:
        content['form']=form
    else:
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
    content['profesor'] = True
   
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
    template_name = 'divermat/cambiocontrasenia.html'
    form_class = PasswordChangeForm
    success_url = 'divermat/perfil.html'
     

@login_required
def setEjercicios(request,idTema=None):
    content={}
    content['registro'] = False
    content['alumno'] = True
    content['profesor'] = False
    tema = Tema.objects.get(id=idTema)
    content['tema'] = tema
    set = []
    ejercicios = Ejercicio.objects.filter(tema=tema)
    j=0
    if len(ejercicios) >= 5:
        while j < 5:
            i = random.randint(0,len(ejercicios)-1)
            ejercicio = ejercicios[i]
            if ejercicio not in set:
                ejercicio_data = {}
                ejercicio_data['id'] = ejercicio.id
                ejercicio_data['enunciado'] = ejercicio.enunciado
                ejercicio_data['titulo'] = ejercicio.titulo
                ejercicio_data['tipo'] = ejercicio.tipo
                ejercicio_data['nsoluciones'] = ejercicio.nsoluciones
                soluciones = ejercicio.soluciones.split(";")
                for solucion in soluciones:
                    solucion_data={}
                    solucion_data['solucion'] = solucion
                    solucion_data['checked'] = False
                    soluciones_data.append(solucion_data)
                ejercicio_data['soluciones'] = soluciones_data
                set.append(ejercicio_data)
                j+=1
    else:
        for ejercicio in ejercicios:
                ejercicio_data = {}
                ejercicio_data['id'] = ejercicio.id
                ejercicio_data['enunciado'] = ejercicio.enunciado
                ejercicio_data['titulo'] = ejercicio.titulo
                ejercicio_data['tipo'] = ejercicio.tipo
                ejercicio_data['nsoluciones'] = ejercicio.nsoluciones
                soluciones = ejercicio.soluciones.split(";")
                soluciones_data=[]
                for solucion in soluciones:
                    solucion_data={}
                    solucion_data['solucion'] = solucion
                    solucion_data['checked'] = False
                    soluciones_data.append(solucion_data)
                ejercicio_data['soluciones'] = soluciones_data
                set.append(ejercicio_data)
    
    if request.method == 'POST':

        if request.user.is_authenticated:
            try:
                alumno = Alumno.objects.get(username=request.user)
                correcto = False
            except Alumno.DoesNotExist:
                alumno = None

        form_data = request.POST
        for ejercicio_data in set:
            ejercicio = Ejercicio.objects.get(id=ejercicio_data['id'])
            if ejercicio.nsoluciones == 1:
                ejercicio_data['resultado'] = "Respuesta incorrecta el resultado esperado era: " + str(ejercicio.solucion_correcta)
                correcto=False
                # if ejercicio.tipo  is 1:
                #     respuesta = form_data.get(str(ejercicio.id))
                # else:
                respuesta = form_data.get(str(ejercicio.id))
                #incluimos en la informacion de las soluciones cuales han sido seleccionadas por el usuario
                soluciones_data=[]
                for solucion in ejercicio.soluciones.split(";"):
                    solucion_data={}
                    solucion_data['solucion'] = solucion
                    solucion_data['checked'] = False
                    if solucion == respuesta:
                        solucion_data['checked'] = True
                    soluciones_data.append(solucion_data)
                ejercicio_data['soluciones'] = soluciones_data
                
                if str(respuesta) == str(ejercicio.solucion_correcta):
                    ejercicio_data['resultado'] = "¡Respuesta Correcta!"
                    correcto=True

            else:
                soluciones_correctas = ejercicio.solucion_correcta.split(";")
                ejercicio_data['resultado'] = "¡Respuesta Correcta!"
                correcto=True
                
                if ejercicio.tipo == 1:

                    respuestas = form_data.getlist(str(ejercicio.id))
                else:

                    respuestas = form_data.get(str(ejercicio.id)).split(";")
                #incluimos en la informacion de las soluciones cuales han sido seleccionadas por el usuario
                soluciones_data=[]
                for solucion in ejercicio.soluciones.split(";"):
                    solucion_data={}
                    solucion_data['solucion'] = solucion
                    solucion_data['checked'] = False
                    if solucion in respuestas:
                        solucion_data['checked'] = True
                    soluciones_data.append(solucion_data)
                ejercicio_data['soluciones'] = soluciones_data
                
                for r in respuestas:
                    flag = False
                    for sol in soluciones_correctas:
                        if str(r) == str(sol):
                            flag = True
                    if(flag == False):
                        ejercicio_data['resultado'] = "Respuesta incorrecta, el resultado esperado era: " + str(soluciones_correctas)  
                        correcto=False 
            
            if alumno:
                añadirEjSeguimientoAlumno(alumno,ejercicio,correcto)                
    
    content['set'] = set

    return render(request,'divermat/setEjercicios.html', context=content)

def examenes(request):
    content = {}
    content['registro'] = False
    content['alumno'] = False
    content['examen'] = False
    if request.user.is_authenticated:
        content = {}
        content['registro'] = False
        content['examen'] = False

        try:
            usuario = Alumno.objects.get(username=request.user)
            return examenesAlumno(usuario,request)
           
        except Alumno.DoesNotExist:
            usuario = None    
    #Si no hay un usuario logeado pero quieren hacer un examen
    else:
        return examenesExterno(request)
    return render(request,'divermat/examenes.html', context=content)


def examenesAlumno(alumno,request):
    content = {}
    content['registro'] = False
    content['examen'] = False
    content['alumno'] = True
    content['examenes'] = Examen.objects.filter(alumno=alumno)

    if request.method == 'POST':
        form = NuevoExamen(request.POST)
        if form.is_valid():

            #Crear un examen que tenga 10 preguntas del tema y curso seleccionado y mostrarlo
            temas = form.cleaned_data['temas']
            crono = form.cleaned_data['crono']

            content['examen_data'] = getExamenAlumno(alumno,temas,crono)

            alumno.numexamen += 1
            nExamen = alumno.numexamen
            content['examen'] = True
            content['n_examen'] = nExamen                    
        else:
            content['error'] = "Error en el formulario"
        
        return render(request,'divermat/examen.html', context=content)      

    else:
        #Usuario iniciada sesion y quiere rellenar el formulario
        c = alumno.curso
        form = NuevoExamen(curso=c)
        
        content['form'] = form

    return render(request,'divermat/examenes.html', context=content)

def examenesExterno(request):
    content = {}
    content['registro'] = False
    content['examen'] = False
    content['alumno'] = False

    if request.method == 'POST':
        form = NuevoExamen(request.POST)
        if form.is_valid():

            #Crear un examen que tenga 10 preguntas del tema y curso seleccionado y mostrarlo
            temas = form.cleaned_data['temas']
            curso = form.cleaned_data['curso'] 
            crono = form.cleaned_data['crono']

            content['examen_data'] = getExamenExterno(temas,curso,crono)

            content['examen'] = True
            content['n_examen'] = 1                    
        else:
            content['error'] = "Error en el formulario"
        
        return render(request,'divermat/examen.html', context=content)      

    else:
        form = NuevoExamen(curso=None)
        content['form'] = form

    return render(request,'divermat/examenes.html', context=content)

def examen(request, examen=None):
    content = {}
    content['profesor'] = False
    content['registro'] = False
    content['nota'] = True
    set = []
    #Obtenemos el Examen
    examen_object = Examen.objects.get(id=examen)
    #Obtenemos los ejercicios del examen para el alumno
    ejercicios_alumno = examen_object.ejercicios.all()
    ejercicios_examen = []

    #Para cada ejercicio del examen para el alumno
    for ejercicio_alumno in ejercicios_alumno:
        #Obtenemos el ejercicio y guardamos los datos que vamos a necesitar en ejercicio_data
        ejercicio = Ejercicio.objects.get(id=ejercicio_alumno.ejercicio.id)
        ejercicios_examen.append(ejercicio)
        ejercicio_data = {}
        ejercicio_data['id'] = ejercicio.id
        ejercicio_data['enunciado'] = ejercicio.enunciado
        ejercicio_data['titulo'] = ejercicio.titulo
        ejercicio_data['tipo'] = ejercicio.tipo
        ejercicio_data['nsoluciones'] = ejercicio.nsoluciones
        #Separamos las posibles soluciones del ejercicio
        soluciones = ejercicio.soluciones.split(";")
        soluciones_data = []
        #En caso de que el ejercicio tenga más de una posible solucion
        if ejercicio.nsoluciones >1:
            soluciones_seleccionadas = ejercicio_alumno.soluciones_seleccionadas
            #Recorremos todas las soluciones y las añadimos al listado de diccionarios soluciones_data
            for solucion in soluciones:
                solucion_data={}
                solucion_data['solucion'] = solucion
                solucion_data['checked'] = False
                if solucion in soluciones_seleccionadas:
                    solucion_data['checked'] = True
                soluciones_data.append(solucion_data)
        else:
            soluciones_seleccionadas = ejercicio_alumno.soluciones_seleccionadas
            for solucion in soluciones:
                solucion_data={}
                solucion_data['solucion'] = solucion
                solucion_data['checked'] = False
                if solucion == soluciones_seleccionadas:
                    solucion_data['checked'] = True
                soluciones_data.append(solucion_data)
        
        #Asignamos las soluciones al ejercicio con un checked a true en caso de que el alumno la hubiese seleccionado
        ejercicio_data['soluciones'] = soluciones_data
        
        #ejercicio_data['soluciones_seleccionadas'] = soluciones_seleccionadas
        #Añadimos la info del ejercicio al set
        set.append(ejercicio_data)

    if request.method == 'POST':
        alumno=None
        if request.user.is_authenticated:
            try:
                alumno = Alumno.objects.get(username=request.user)
                correcto = False
                content['alumno'] = True
            except Alumno.DoesNotExist:
                alumno = None

        form_data = request.POST
        ejercicios_correctos = 0
        for ejercicio_data in set:
            ejercicio = Ejercicio.objects.get(id=ejercicio_data['id'])
            if ejercicio.nsoluciones == 1:
                ejercicio_data['resultado'] = "Respuesta incorrecta el resultado esperado era: " + str(ejercicio.solucion_correcta)
                correcto=False
                # if ejercicio.tipo  is 1:
                #     respuesta = form_data.get(str(ejercicio.id))
                # else:
                respuesta = form_data.get(str(ejercicio.id))
                
                for ej_alum in ejercicios_alumno:
                    if ej_alum.ejercicio == ejercicio:
                        ej_alum.soluciones_seleccionadas = respuesta
                        ej_alum.save()
                
                #incluimos en la informacion de las soluciones cuales han sido seleccionadas por el usuario
                soluciones_data=[]
                for solucion in ejercicio.soluciones.split(";"):
                    solucion_data={}
                    solucion_data['solucion'] = solucion
                    solucion_data['checked'] = False
                    if solucion == respuesta:
                        solucion_data['checked'] = True
                    soluciones_data.append(solucion_data)
                ejercicio_data['soluciones'] = soluciones_data
        
                if str(respuesta) == str(ejercicio.solucion_correcta):
                    ejercicio_data['resultado'] = "¡Respuesta Correcta!"
                    correcto=True

            else:
                soluciones_correctas = ejercicio.solucion_correcta.split(";")
                ejercicio_data['resultado'] = "¡Respuesta Correcta!"
                correcto=True

                for ej_alum in ejercicios_alumno:
                    if ej_alum.ejercicio == ejercicio:
                        ej_alum.soluciones_seleccionadas = form_data.getlist(str(ejercicio.id))
                        ej_alum.save()

                if ejercicio.tipo == 1:

                    respuestas = form_data.getlist(str(ejercicio.id))
                else:

                    respuestas = form_data.get(str(ejercicio.id)).split(";")
                #incluimos en la informacion de las soluciones cuales han sido seleccionadas por el usuario
                soluciones_data=[]
                for solucion in ejercicio.soluciones.split(";"):
                    solucion_data={}
                    solucion_data['solucion'] = solucion
                    solucion_data['checked'] = False
                    if solucion in respuestas:
                        solucion_data['checked'] = True
                    soluciones_data.append(solucion_data)
                ejercicio_data['soluciones'] = soluciones_data

                if len(respuestas) >0:    
                    
                    for r in respuestas:
                        flag = False

                        for sol in soluciones_correctas:
                            if str(r) == str(sol):
                                flag = True
                        if(flag == False):
                            ejercicio_data['resultado'] = "Respuesta incorrecta, el resultado esperado era: " + str(soluciones_correctas)  
                            correcto=False 
                else:
                    ejercicio_data['resultado'] = "Respuesta incorrecta, el resultado esperado era: " + str(soluciones_correctas)  
                    correcto=False 

            
            if alumno:
                añadirEjSeguimientoAlumno(alumno,ejercicio,correcto)   
            if correcto:
                ejercicios_correctos += 1
        if ejercicios_correctos > 0:
            examen_object.nota = (ejercicios_correctos*100)/len(ejercicios_alumno)
            examen_object.save()
        else:
            examen_object.nota = 0
            examen_object.save()

    examen_data={}
    examen_data['ejercicios'] = set
    examen_data['examen'] = examen_object
    content['examen_data']=examen_data
    #SI hay user authenticated poner Alumno a True
    return render(request,'divermat/examen.html', context=content)

def videos(request):
    #Mostrar en pequeño la ventana del video
    content = {}
    content['registro'] = False
    content['alumno'] = False
    content['Tipo'] = 'Videos'
    content['Contenido'] = {}
    todos_videos = Video.objects.all()
    temas = []
    for tema in Tema.objects.all():
        temas.append(tema.titulo)
    content['temas'] = temas
  
    if request.user.is_authenticated:
        try:
            alumno = Alumno.objects.get(username=request.user)
            content['alumno'] = True
            content['profesor'] = False
            todos_videos = Video.objects.filter(curso=alumno.curso)

            temas = []
            for tema in Tema.objects.filter(curso=alumno.curso):
                temas.append(tema.titulo)
            content['temas'] = temas

        except Alumno.DoesNotExist:
            alumno = None
            content['alumno'] = False
            content['profesor'] = True

    content['Contenido'] = getFilteredContent(todos_videos,request)


    return render(request,'divermat/inicio.html', context=content,)

#Mostrar el video como tal
def video(request,idVideo):
    content = {}
    content['registro'] = False
    content['alumno'] = False
    content['video'] = Video.objects.get(id=idVideo)

    return render(request,'divermat/video.html',content)


def resumenes(request):

    content = {}
    content['registro'] = False
    content['alumno'] = False
    content['Tipo'] = 'Resúmenes'
    content['Contenido'] = {}
    todos_res = Resumen.objects.all()

    temas = []
    for tema in Tema.objects.all():
        temas.append(tema.titulo)
    content['temas'] = temas
    
    if request.user.is_authenticated:
        try:
            alumno = Alumno.objects.get(username=request.user)
            todos_res = Resumen.objects.filter(curso=alumno.curso)
            content['alumno'] = True
            content['profesor'] = False

            temas = []
            for tema in Tema.objects.filter(curso=alumno.curso):
                temas.append(tema.titulo)
            content['temas'] = temas

        except Alumno.DoesNotExist:
            alumno = None
            content['alumno'] = False
            content['profesor'] = True

    content['Contenido'] = getFilteredContent(todos_res,request)
    
    return render(request,'divermat/inicio.html', context=content,)


#Mostrar el resumen como tal
def resumen(request,idResumen):
    content = {}
    content['registro'] = False
    content['alumno'] = False
    content['resumen'] = Resumen.objects.get(id=idResumen)

    return render(request,'divermat/resumen.html', content )


#Mostrar el ejercicio como tal para obtener respuesta del usuario
def ejercicio(request, ejercicio=None):
    content = {}
    content['registro'] = False
    alumno = None
    if request.user.is_authenticated:
        try:
            alumno = Alumno.objects.get(username=request.user)
            correcto = False
        except Alumno.DoesNotExist:
            alumno = None
    if ejercicio:
        content['ejercicio'] = Ejercicio.objects.get(id=ejercicio)
        ejercicio = Ejercicio.objects.get(id=ejercicio)
        soluciones = ejercicio.soluciones.split(";")
        content['soluciones'] = []
        solucion_seleccionada = request.GET.getlist('solucion', [])

        for solucion in soluciones:
            solucion_data={}
            solucion_data['solucion'] = solucion
            solucion_data['checked'] = False
            if solucion in solucion_seleccionada:
                solucion_data['checked'] = True

            content['soluciones'].append(solucion_data)

        if solucion_seleccionada:
            if ejercicio.nsoluciones == 1:
                
                if str(ejercicio.solucion_correcta) == str(solucion_seleccionada[0]):
                    content['resultado'] = "¡Respuesta correcta!"
                    correcto = True
                else:
                    content['resultado'] = "Respuesta incorrecta, el resultado esperado era: " + str(ejercicio.solucion_correcta)
                    correcto = False
            else:
                content['resultado'] = "¡Respuesta correcta!"
                correcto = True
                soluciones_correctas = ejercicio.solucion_correcta.split(";")
                for el in solucion_seleccionada:
                    flag = False
                    for sol in soluciones_correctas:
                        if str(el) == str(sol):
                            flag = True
                    if(flag == False):
                        content['resultado'] = "Respuesta incorrecta, el resultado esperado era: " + str(soluciones_correctas)
                        correcto = False
            if alumno!=None:
                añadirEjSeguimientoAlumno(alumno,ejercicio,correcto)

    return render(request,'divermat/ejercicio.html', context=content)

@login_required
def clases(request):

    content = {}
    content['registro'] = False
    profesor = Profesor.objects.get(username=request.user)
    content['profesor'] = True
    content['alumno'] = False
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
                alumno.centro = profesor.centro
                alumno.curso = curso
                alumno.clase = clase
                alumno.numexamen = 0
                alumno.tipo = True
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
    content['profesor'] = True
    content['alumnos'] = []
    
    alumnos = Alumno.objects.all()
    if busqueda and busqueda != "Buscar Alumno":
        alumnos_filtered = []
        for a in alumnos:
            if unidecode(busqueda.lower()) in unidecode(a.first_name.lower()) or unidecode(busqueda.lower()) in unidecode(a.last_name.lower()):
                alumnos_filtered.append(a)            
            elif unidecode(busqueda.lower()) in unidecode(a.username.lower()) or unidecode(busqueda.lower()) in unidecode(a.centro.lower()):  
                alumnos_filtered.append(a) 
        alumnos = alumnos_filtered

    if filtro and filtro != "Curso":
        alumnos_filtered=[]
        for a in alumnos:
            if str(a.curso)+"º ESO" == filtro:
                alumnos_filtered.append(a)
        alumnos=alumnos_filtered
    content['alumnos'] = alumnos

    if alumno:
        for alum in Alumno.objects.all():
            if alum.id == int(alumno):
                content['alumno'] = alum
                break
        content['informacion'] = Seguimiento.objects.filter(alumno=alum)
        
    return render(request,'divermat/alumnos.html', context=content,)

@login_required
def contenido(request):
    content = {}
    content['registro'] = False

    try :
        profesor = Profesor.objects.get(username=request.user)
        content['profesor'] = True
        content['alumno'] = False

    except Profesor.DoesNotExist:
        content['profesor'] = False
    
    content['videos'] = Video.objects.all()
    content['resumenes'] = Resumen.objects.all()
    temas = []
    for tema in Tema.objects.all():
        temas.append(tema.titulo)
    content['temas'] = temas

    todos_videos = Video.objects.all()
    todos_res = Resumen.objects.all()

    content['videos'] = getFilteredContent(todos_videos,request)
    content['resumenes'] = getFilteredContent(todos_res,request)

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
    content['profesor'] = True
    content['alumno'] = False

    alumnos = getAlumnosClase(int(clase.id))

    content['alumnos'] = alumnos
    #Esto hay que comprobarlo cuando seguimiento tenga info en alumnos 
    informacion = []
    for t in Tema.objects.filter(curso=clase.curso):
        informacion.append(calcularAcierto(t,clase))
    content['informacion'] = informacion

    return render(request,'divermat/clase.html', context=content,)

@login_required
def claseAlumno(request,clase=None):
    content = {}
    content['registro'] = False
    content['clase'] = clase
    content['curso'] = clase.curso
    content['ano_academico'] = clase.ano_academico
    content['nombre'] = clase.nombre
    content['nalumnos'] = clase.n_alumnos
    content['centro'] = clase.centro
    content['ejercicios'] = clase.ejercicios
    content['alumno'] = True
    content['profesor'] = False

    return render(request,'divermat/clase.html', context=content,)

@login_required
def infoclase(request, claseid=None):
    content={}
    content['registro'] = False
    content['profesor'] = True
    content['alumno'] = False
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
                    if curso != "" and curso !=None:
                        c.curso = curso
                        c.save()
                    if ano_academico != None and ano_academico!="":
                        c.ano_academico = ano_academico
                        c.save()
                    if nombre != "" and nombre !=None:
                        print(nombre)
                        c.nombre = nombre
                        c.save()
                    if centro != "" and centro != None:
                        c.centro = centro
                        c.save()

                    return clase(request,claseid)
        
    content['form'] = NuevaInfoClase()
    
    return render(request,'divermat/nuevainfoclase.html', context=content,)

@login_required
def alumnosclase(request, claseid=None):
    content={}
    content['registro'] = False
    content['profesor'] = True
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
                alumno.tipo = True
                alumno.save()
        
    form = NuevoAlumno(None,None)
    content['form'] = form
    
    return render(request,'divermat/alumnosclase.html', context=content,)

@login_required
def seguimientoclase(request, claseid=None):
    content={}
    content['registro'] = False
    content['profesor'] = True
    content['alumno'] = False

    if claseid:
        for c in Clase.objects.all():
            if c.id == int(claseid):
                flag = True
                break

        if flag:  
            informacion = []
            for t in Tema.objects.filter(curso=c.curso):
                informacion.append(calcularAcierto(t,c))
            content['informacion'] = informacion
            #Comprobarlo cuando estén los alumnos listos
            content['ejercicios_asignados'] = c.ejercicios.all()

    return render(request,'divermat/seguimientoclase.html', context=content,)

#Metodos que se usan internamente

def calcularAcierto(tema,clase):
    alumnos = getAlumnosClase(clase.id)
    infor = {}
    infor['tema'] = str(tema.tema) + " " + tema.titulo
    acierto = 0
    n_ejercicios = 0
    for alumno in alumnos:
        for segui in Seguimiento.objects.filter(alumno=alumno):
            if segui.tema == tema:
                acierto += segui.acierto
                n_ejercicios += segui.n_ejercicios
                break
    infor['acierto'] = round(acierto/clase.n_alumnos,2)
    infor['ejercicios'] = n_ejercicios
    return infor

def getAlumnosClase(claseid):

    clase = Clase.objects.filter(id=claseid)[0]
    alumnos = Alumno.objects.filter(clase=clase)
    return alumnos

def getFilteredContent(todos_elem,request):
    contenido = []
    contenFinal = []
    for elem in todos_elem:
        conten = {}
        conten['id'] = elem.id
        conten['titulo'] = elem.titulo
        contenido.append(conten)
        contenFinal = contenido

    busqueda = request.GET.get('buscar', '')
    curso = request.GET.get('curso', '')
    tema = request.GET.get('tema', '')
    tipo = request.GET.get('tipo', '')

  
    elem_filtrados = []
    if busqueda and busqueda != "Buscar":
        contenido = []
        elem_filtrados = []
        for elem in todos_elem:
            if unidecode(busqueda.lower()) in unidecode(elem.titulo.lower()):
                conten = {}
                conten['id'] = elem.id
                conten['titulo'] = elem.titulo
                contenido.append(conten)
                elem_filtrados.append(elem)
        contenFinal = contenido
        todos_elem=elem_filtrados

    if curso and curso != "Curso":
        contenido = []
        elem_filtrados = []
        for elem in todos_elem:
            if str(curso[0]) == str(elem.curso):
                conten = {}
                conten['id'] = elem.id
                conten['titulo'] = elem.titulo
                contenido.append(conten)
                elem_filtrados.append(elem)
        contenFinal = contenido
        todos_elem=elem_filtrados

    if tema and tema != "Tema":
        contenido = []
        elem_filtrados = []
        for elem in todos_elem:
            if str(tema) in str(elem.tema):
                conten = {}
                conten['id'] = elem.id
                conten['titulo'] = elem.titulo
                contenido.append(conten)
                elem_filtrados.append(elem)
        contenFinal = contenido
        todos_elem=elem_filtrados

    if tipo and tipo != "Tipo":
        contenido = []
        elem_filtrados = []
        if tipo == "Test":
            tipos = 1
        elif tipo == "Respuesta corta":
            tipos = 2
        else:
            tipos = 3
        for elem in todos_elem:
            if tipos == elem.tipo:
                conten = {}
                conten['id'] = elem.id
                conten['titulo'] = elem.titulo
                contenido.append(conten)
                elem_filtrados.append(elem)
        contenFinal = contenido
        todos_elem=elem_filtrados

    return contenFinal
   
def getExamenAlumno(usuario,temas,crono):
    #Dividimos los 10 ejercicios totales entre el total de temas para saber el nº de ej por tema
    nejercicios = 10/len(temas)
    ejercicios_examen = []
    temas_examen = []
    titulo = ""
    #Recorremos los ids de los temas seleccionados para el examen
    for t in temas:
        tema = Tema.objects.get(id=t.id)
        if tema:
            #Añadimos el tema a la lista de temas del examen
            temas_examen.append(tema.id)
            #Concatenamos el tema en el título del examen
            titulo += ", "+ str(tema.tema)
            #Obtenemos los ejercicios de ese tema
            ejer_tema = Ejercicio.objects.filter(tema=tema)
            #Si hay más ejercicios de los requeridos
            if len(ejer_tema) >= nejercicios:
                j=0
                while j < nejercicios:
                    #Obtenemos número aleatorio que servirá como índice para coger un ejercicio
                    i = random.randint(0,len(ejer_tema)-1)
                    ejercicio = ejer_tema[i]
                    #Si el ejercicio no está ya lo añadimos a la lista de ejs del examen
                    if ejercicio not in ejercicios_examen:
                        ejercicios_examen.append(ejercicio)
                        j+=1
            #Si hay menos ejercicios de los requeridos
            else:
                #Recorremos todos los ejercicios del tema
                for ejercicio in ejer_tema:
                    #Si el ejercicio todavía no está en el examen lo añadimos a la lista
                    if ejercicio not in ejercicios_examen:
                        ejercicios_examen.append(ejercicio)
    #Creamos el objeto del examen
    examen = Examen.objects.create(titulo="Examen de los temas" + titulo,alumno=usuario,curso=usuario.curso,tiempo=0)
    examen.save()
    
    content = {}
    content['examen'] = examen
    content['ejercicios'] = []

    #Recorremos la lista de ejercicios del examen
    for ejercicio in ejercicios_examen:
        #Creamos el objeto de tipo ejercicio alumno y lo añadimos al examen
        ejercicioAlumno = EjercicioUsuario.objects.create(ejercicio=ejercicio,alumno=usuario,soluciones_seleccionadas="")
        examen.ejercicios.add(ejercicioAlumno)
        #Guardamos la información relevante de los ejercicios en el diccionario a mostrar en el html
        ejercicio_data = {}
        ejercicio_data['id'] = ejercicio.id
        ejercicio_data['enunciado'] = ejercicio.enunciado
        ejercicio_data['titulo'] = ejercicio.titulo
        ejercicio_data['tipo'] = ejercicio.tipo
        ejercicio_data['nsoluciones'] = ejercicio.nsoluciones
        soluciones = ejercicio.soluciones.split(";")
        ejercicio_data['soluciones'] = []
        for solucion in soluciones:
            solucion_data = {}
            solucion_data['solucion'] = solucion
            solucion_data['checked'] = False
            ejercicio_data['soluciones'].append(solucion_data)

        content['ejercicios'].append(ejercicio_data)
    
    examen.temas.set(temas_examen)
    examen.save()

    return content

def getExamenExterno(temas,curso,crono):
#Dividimos los 10 ejercicios totales entre el total de temas para saber el nº de ej por tema
    nejercicios = 10/len(temas)
    ejercicios_examen = []
    temas_examen = []
    titulo = ""
    ejercicios = []
    #Recorremos los ids de los temas seleccionados para el examen
    for t in temas:
        tema = Tema.objects.get(id=t.id)
        if tema:
            #Añadimos el tema a la lista de temas del examen
            temas_examen.append(tema.id)
            #Concatenamos el tema en el título del examen
            titulo += ", "+ str(tema.tema)
            #Obtenemos los ejercicios de ese tema
            ejer_tema = Ejercicio.objects.filter(tema=tema)
            #Si hay más ejercicios de los requeridos
            if len(ejer_tema) >= nejercicios:
                j=0
                while j < nejercicios:
                    #Obtenemos número aleatorio que servirá como índice para coger un ejercicio
                    i = random.randint(0,len(ejer_tema)-1)
                    ejercicio = ejer_tema[i]
                    #Si el ejercicio no está ya lo añadimos a la lista de ejs del examen
                    if ejercicio not in ejercicios_examen:
                        ejercicios_examen.append(ejercicio)
                        j+=1
            #Si hay menos ejercicios de los requeridos
            else:
                #Recorremos todos los ejercicios del tema
                for ejercicio in ejer_tema:
                    #Si el ejercicio todavía no está en el examen lo añadimos a la lista
                    if ejercicio not in ejercicios_examen:
                        ejercicios_examen.append(ejercicio)
    #Creamos el objeto del examen
    examen = Examen.objects.create(titulo="Examen de los temas" + titulo,alumno=None,curso=curso,tiempo=0)
    examen.save()
    
    content = {}
    content['examen'] = examen
    content['ejercicios'] = []

    #Recorremos la lista de ejercicios del examen
    for ejercicio in ejercicios_examen:
        #Creamos el objeto de tipo ejercicio alumno y lo añadimos al examen
        ejercicioAlumno = EjercicioUsuario.objects.create(ejercicio=ejercicio,alumno=None,soluciones_seleccionadas="")
        examen.ejercicios.add(ejercicioAlumno)
        #Guardamos la información relevante de los ejercicios en el diccionario a mostrar en el html
        ejercicio_data = {}
        ejercicio_data['id'] = ejercicio.id
        ejercicio_data['enunciado'] = ejercicio.enunciado
        ejercicio_data['titulo'] = ejercicio.titulo
        ejercicio_data['tipo'] = ejercicio.tipo
        ejercicio_data['nsoluciones'] = ejercicio.nsoluciones
        soluciones = ejercicio.soluciones.split(";")
        ejercicio_data['soluciones'] = []
        for solucion in soluciones:
            solucion_data = {}
            solucion_data['solucion'] = solucion
            solucion_data['checked'] = False
            ejercicio_data['soluciones'].append(solucion_data)

        content['ejercicios'].append(ejercicio_data)
    
    examen.temas.set(temas_examen)
    examen.save()

    return content

def añadirEjSeguimientoAlumno(alumno,ejercicio,correcto):
    try:
        seguimiento_alumno = Seguimiento.objects.get(alumno=alumno, tema=ejercicio.tema)
        n_ej_correctos = seguimiento_alumno.acierto*seguimiento_alumno.n_ejercicios/100
        seguimiento_alumno.n_ejercicios += 1
        if correcto:
            seguimiento_alumno.acierto = (n_ej_correctos+1)*100/seguimiento_alumno.n_ejercicios
        else:
            seguimiento_alumno.acierto = (n_ej_correctos*100)/seguimiento_alumno.n_ejercicios

    except Seguimiento.DoesNotExist:
        seguimiento_alumno = Seguimiento()
        seguimiento_alumno.alumno=alumno
        seguimiento_alumno.tema=ejercicio.tema
        seguimiento_alumno.n_ejercicios = 1
        if correcto:
            seguimiento_alumno.acierto = 100
        else:
            seguimiento_alumno.acierto = 0
    seguimiento_alumno.acierto=round(seguimiento_alumno.acierto,2)
    seguimiento_alumno.save()
    seguimiento_alumno.ejercicios.add(ejercicio)
    seguimiento_alumno.save()

    return seguimiento_alumno