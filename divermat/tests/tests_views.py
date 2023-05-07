from datetime import datetime
import pickle

from django.test import TestCase
from django.urls import reverse
from django.test import Client
from os.path import join

from divermat.forms import (NuevoExamen,NuevoSetEjercicios, 
                            NuevaClase,NuevaInfoProfesor, NuevaInfoAlumno,
                            NuevaInfoClase,NuevoAlumno,InicioSesion)

from divermat.models import *

from divermat.views import *
from divermat.urls import *


class ViewsTestsWithNoUserLoggedIn(TestCase):
    """En esta clase vamos a probar el correcto funcionamiento de las vistas que no requieren un usuario loggeado"""
    @classmethod
    def setUpTestData(self):
        self.curso = Curso.objects.create(curso=1)
        self.curso2 = Curso.objects.create(curso=2)
        self.tema = Tema.objects.create(tema=1, curso=self.curso, titulo="Números Naturales")
        self.tema2 = Tema.objects.create(tema=3, curso=self.curso2, titulo="Ecuaciones")
        self.profesor = Profesor.objects.create(username="profe",first_name="Profesor", last_name="Prueba", tipo=0)
        self.ejercicio = Ejercicio.objects.create(curso=self.curso,tema=self.tema,titulo="Suma de números enteros",tipo=2,enunciado="¿Cuánto es 2+2?",soluciones="4",nsoluciones=1,solucion_correcta=4)
        self.ejercicio2 = Ejercicio.objects.create(curso=self.curso2,tema=self.tema2,titulo="Ecuaciones de primer grado",tipo=1,enunciado="¿Cuánto es x-2=2?",soluciones="2;4;3;5",nsoluciones=1,solucion_correcta=4)
        self.clase = Clase.objects.create(curso=self.curso,nombre="A",centro="IES Prueba",ano_academico=datetime.now(), n_alumnos=1,profesor=self.profesor)
        self.alumno = Alumno.objects.create(username="alumno",first_name="Alumno",last_name="Prueba",tipo=1,password_temporal="1234", curso=self.curso, clase=self.clase)
        self.ejercicioUsuario = EjercicioUsuario.objects.create(ejercicio=self.ejercicio, alumno=self.alumno, soluciones_seleccionadas="4",resultado="¡Respuesta Correcta!")
        self.examen= Examen.objects.create(titulo="Examen tema 1", alumno=self.alumno,curso=self.curso,cronometrado=False,nota=100,inicio=datetime.now(timezone.utc))
        temas = []
        temas.append(self.tema.id)
        self.examen.temas.set(temas)
        ejerciciosAlumno = []
        ejerciciosAlumno.append(self.ejercicioUsuario.id)
        self.examen.ejercicios.set(ejerciciosAlumno)
        self.examen.save()
        self.seguimiento = Seguimiento.objects.create(alumno=self.alumno, tema=self.tema, n_ejercicios=1, acierto=100)
        ejercicios = []
        ejercicios.append(self.ejercicio.id)
        self.seguimiento.ejercicios.set(ejercicios)
        self.seguimiento.save()
        # self.video = Video.objects.create(curso=self.curso,tema=self.tema,titulo="Resolución de sumas de Números naturales",video=None)
        self.resumen = Resumen.objects.create(texto="........",curso=self.curso,tema=self.tema,titulo="Resolución de sumas de Números naturales")
        self.resumen = Resumen.objects.create(texto="........2",curso=self.curso2,tema=self.tema2,titulo="Resolución de ecuaciones de primer grado")

    def test_all_urls_are_correct(self):
        """Probamos que todas las urls que pueden ser accedidas
        por usuarios sin cuenta dan 200 OK"""
        #Si se introduce un id que no existe se redirige a examenes
        respuesta = self.client.get('/divermat/examen/1/')
        self.assertEqual(respuesta.status_code, 200)
        #Redirige a la página de inicio
        respuesta = self.client.get('/divermat/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/index')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/Ejercicios')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/iniciar_sesion/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/registro/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/Videos/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/videos/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/Resúmenes/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/resumenes/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/examenes/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejercicio/1/')
        self.assertEqual(respuesta.status_code, 200)
        # respuesta = self.client.get('/divermat/video/1/')
        # self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/resumen/1/')
        self.assertEqual(respuesta.status_code, 200)
    
    def test_urls_when_wrong_param(self):
        """Probamos que todas las urls que pueden ser accedidas
        por usuarios sin cuenta con un parametro con valor no válido o no existente dan 200 OK"""
        #Si se introduce un id que no existe se redirige a examenes
        respuesta = self.client.get('/divermat/examen/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/examen/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejercicio/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejercicio/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        # respuesta = self.client.get('/divermat/video/1/',follow=True)
        # self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/resumen/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/resumen/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)

    def test_all_urls_names_are_correct(self):
        """Probamos que todas las urls que pueden ser accedidas por
        usuarios no loggeados y son accedidas a través del nombre dan 200 OK"""
        respuesta = self.client.get(reverse('index'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('iniciar_sesion'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('registro'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('examen',kwargs={'examen':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('examenes'))
        self.assertEqual(respuesta.status_code, 200)
        # respuesta = self.client.get('/divermat/video/1/')
        # self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('videos'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('resumenes'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('resumen',kwargs={'idResumen':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}))
        self.assertEqual(respuesta.status_code, 200)

    def test_returned_templates_are_correct(self):
        """Probamos que las templates devueltas son las esperadas para un usuario no loggeado
        y probamos los redirect en caso de que los argumentos pasados no sean correctos"""
        respuesta = self.client.get(reverse('index'))
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('iniciar_sesion'))
        self.assertTemplateUsed(respuesta, 'divermat/inicio_sesion.html')
        respuesta = self.client.get(reverse('registro'))
        self.assertTemplateUsed(respuesta, 'divermat/registro.html')
        respuesta = self.client.get(reverse('examen',kwargs={'examen':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/examen.html')
        #Si el examen no existe se hace un redirect a examenes
        respuesta = self.client.get(reverse('examen',kwargs={'examen':3,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/examenes.html')
        respuesta = self.client.get(reverse('examenes'))
        self.assertTemplateUsed(respuesta, 'divermat/examenes.html')
        respuesta = self.client.get(reverse('videos'))
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('resumenes'))
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('resumen',kwargs={'idResumen':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/resumen.html')
        #Si el resumen no existe se hace redirect a index
        respuesta = self.client.get(reverse('resumen',kwargs={'idResumen':3,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/ejercicio.html')
    

class ViewsTestsWithAlumnoLoggedIn(TestCase):
    """En esta clase vamos a probar el correcto funcionamiento de las vistas cuando un alumno está loggeado"""
    @classmethod
    def setUpTestData(self):
        self.curso = Curso.objects.create(curso=1)
        self.curso2 = Curso.objects.create(curso=2)
        self.tema = Tema.objects.create(tema=1, curso=self.curso, titulo="Números Naturales")
        self.tema2 = Tema.objects.create(tema=3, curso=self.curso2, titulo="Ecuaciones")
        self.profesor = Profesor.objects.create(username="profe",first_name="Profesor", last_name="Prueba", tipo=0)
        self.ejercicio = Ejercicio.objects.create(curso=self.curso,tema=self.tema,titulo="Suma de números enteros",tipo=2,enunciado="¿Cuánto es 2+2?",soluciones="4",nsoluciones=1,solucion_correcta=4)
        self.ejercicio2 = Ejercicio.objects.create(curso=self.curso2,tema=self.tema2,titulo="Ecuaciones de primer grado",tipo=1,enunciado="¿Cuánto es x-2=2?",soluciones="2;4;3;5",nsoluciones=1,solucion_correcta=4)
        self.clase = Clase.objects.create(curso=self.curso,nombre="A",centro="IES Prueba",ano_academico=datetime.now(), n_alumnos=1,profesor=self.profesor)
        self.alumno = Alumno.objects.create(username="testAlumno",first_name="Alumno",last_name="Prueba",tipo=1, curso=self.curso, clase=self.clase, password="1234")
        self.alumno.save()
        self.alumno2 = Alumno.objects.create(username="testAlumno2",first_name="Alumno2",last_name="Prueba",tipo=1,password_temporal="1234", curso=self.curso, clase=self.clase)
        self.ejercicioUsuario = EjercicioUsuario.objects.create(ejercicio=self.ejercicio, alumno=self.alumno, soluciones_seleccionadas="4",resultado="¡Respuesta Correcta!")
        self.examen= Examen.objects.create(titulo="Examen tema 1", alumno=self.alumno,curso=self.curso,cronometrado=False,nota=100,inicio=datetime.now(timezone.utc))
        temas = []
        temas.append(self.tema.id)
        self.examen.temas.set(temas)
        ejerciciosAlumno = []
        ejerciciosAlumno.append(self.ejercicioUsuario.id)
        self.examen.ejercicios.set(ejerciciosAlumno)
        self.examen.save()
        self.seguimiento = Seguimiento.objects.create(alumno=self.alumno, tema=self.tema, n_ejercicios=1, acierto=100)
        ejercicios = []
        ejercicios.append(self.ejercicio.id)
        self.seguimiento.ejercicios.set(ejercicios)
        self.seguimiento.save()
        # self.video = Video.objects.create(curso=self.curso,tema=self.tema,titulo="Resolución de sumas de Números naturales",video=None)
        self.resumen = Resumen.objects.create(texto="........",curso=self.curso,tema=self.tema,titulo="Resolución de sumas de Números naturales")
        self.resumen = Resumen.objects.create(texto="........2",curso=self.curso2,tema=self.tema2,titulo="Resolución de ecuaciones de primer grado")
    
    def test_all_urls_are_correct_for_students(self):
        """Probamos que todas las urls que pueden ser accedidas
        por alumnos dan 200 OK"""
        login = self.client.force_login(self.alumno)
        respuesta = self.client.get('/divermat/perfil/')
        self.assertEqual(respuesta.status_code, 200)
        #Redirige a la página de inicio
        respuesta = self.client.get('/divermat/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/index')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/Ejercicios')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/iniciar_sesion/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/registro/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/1/1/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/1/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejercicio/1/')
        self.assertEqual(respuesta.status_code, 200)
        # respuesta = self.client.get('/divermat/video/1/')
        # self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/resumen/1/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/clase/1',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/clase',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/cambiar_contrasenia/')
        self.assertEqual(respuesta.status_code, 200)
        #Estas pantallas son sólo del profesor
        respuesta = self.client.get('/divermat/alumnosclase/1/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/seguimientoclase/1/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/alumnos/1/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/alumnos',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/contenido',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/seguimientoalumnoclase/1/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/clases',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/infoclase/1/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        #Estas pantallas son de Alumnos o usuarios sin registrar por lo que redirige al profesor a index
        respuesta = self.client.get('/divermat/Videos/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/videos/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/Resúmenes/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/resumenes/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/examenes/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/cambiarInformacionAlumno/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/setEjercicios/1/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/examen/1/')
        self.assertEqual(respuesta.status_code, 200)
        #Esta pantalla cierra sesión y nos redirige al index por lo que se usa follow=True
        respuesta = self.client.get('/divermat/cerrar_sesion/',follow=True)
        self.assertEqual(respuesta.status_code, 200)

    def test_urls_when_wrong_param_for_students(self):
        """Probamos que todas las urls que pueden ser accedidas
        por alumnos con un parametro con valor no válido o no existente dan 200 OK"""
        login = self.client.force_login(self.alumno)

        respuesta = self.client.get('/divermat/ejerciciosAsignados/a/1/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/1/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/a/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/10/1/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/1/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/10/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejercicio/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejercicio/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        # respuesta = self.client.get('/divermat/video/1/',follow=True)
        # self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/resumen/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/resumen/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/clase/a',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/clase/10',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        #Estas pantallas son sólo del profesor
        respuesta = self.client.get('/divermat/alumnosclase/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/alumnosclase/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/seguimientoclase/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/seguimientoclase/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/alumnos/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/alumnos/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/seguimientoalumnoclase/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/seguimientoalumnoclase/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/infoclase/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/infoclase/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        #Estas pantallas son de Alumnos o usuarios sin registrar por lo que redirige al profesor a index
        respuesta = self.client.get('/divermat/setEjercicios/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/setEjercicios/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/examen/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/examen/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        self.client.logout()

    def test_all_urls_names_are_correct_for_students(self):
        """Probamos que todas las urls que pueden ser accedidas por
        alumnos y son accedidas a través del nombre dan 200 OK"""
        login = self.client.force_login(self.alumno)
        respuesta = self.client.get(reverse('perfil'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('index'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('iniciar_sesion'),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('registro'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('ejerciciosAsignados',kwargs={'claseid':1,'ejercicioid':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('ejerciciosAsignados',kwargs={'claseid':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('ejerciciosAsignados'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}))
        self.assertEqual(respuesta.status_code, 200)
        # respuesta = self.client.get(reverse('video',kwargs={'idVideo':1,}))
        # self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('resumen',kwargs={'idResumen':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('clase',kwargs={'clase':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('clase'),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('cambiar_contrasenia'))
        self.assertEqual(respuesta.status_code, 200)
        #Estas pantallas son del profesor por lo que nos redirige a index
        respuesta = self.client.get(reverse('seguimientoalumnoclase',kwargs={'alumnoid':1,}),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('clases'), follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('alumnosclase',kwargs={'claseid':1,}),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('seguimientoclase',kwargs={'claseid':1,}),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('alumnos',kwargs={'alumno':1,}),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('alumnos'),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('contenido'),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('infoclase',kwargs={'claseid':1,}),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        #Estas pantallas son de Alumnos o usuarios sin registrar por lo que redirige al profesor a index
        respuesta = self.client.get(reverse('setEjercicios',kwargs={'idTema':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('examen',kwargs={'examen':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('videos'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('resumenes'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('examenes'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('cambiarInformacionAlumno'))
        self.assertEqual(respuesta.status_code, 200)
        #Esta pantalla cierra sesión y nos redirige al index por lo que se usa follow=True
        respuesta = self.client.get(reverse('cerrar_sesion'),follow=True)
        self.assertEqual(respuesta.status_code, 200)

    def test_returned_templates_are_correct(self):
        """Probamos que las templates devueltas son las esperadas para un alumno
        y probamos los redirect en caso de que los argumentos pasados no sean correctos"""
        login = self.client.force_login(self.alumno)
        respuesta = self.client.get(reverse('perfil'))
        self.assertTemplateUsed(respuesta, 'divermat/perfil.html')
        respuesta = self.client.get(reverse('index'))
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('iniciar_sesion'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('registro'))
        self.assertTemplateUsed(respuesta, 'divermat/registro.html')
        respuesta = self.client.get(reverse('ejerciciosAsignados',kwargs={'claseid':1,'ejercicioid':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosAsignadosAlumno.html')
        respuesta = self.client.get(reverse('ejerciciosAsignados',kwargs={'claseid':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosAsignadosAlumno.html')
        respuesta = self.client.get(reverse('ejerciciosAsignados'))
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosAsignadosAlumno.html')
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/ejercicio.html')
        #Probamos un ejercicio que no existe y debe redirigirnos al inicio
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':2,}))
        self.assertTemplateUsed(respuesta, 'divermat/ejercicio.html')
        # respuesta = self.client.get(reverse('video',kwargs={'idVideo':1,}))
        # self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('resumen',kwargs={'idResumen':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/resumen.html')
        #Probamos un resumen que no exitse y vacio y debe rediriginros la index
        respuesta = self.client.get(reverse('resumen',kwargs={'idResumen':3,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('clase',kwargs={'clase':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/clase.html')
        #Probamos si no se indica el id de la clase
        respuesta = self.client.get(reverse('clase'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('cambiar_contrasenia'))
        self.assertTemplateUsed(respuesta, 'divermat/cambiocontrasenia.html')
        #Estas pantallas son del profesor por lo que nos redirige a index
        respuesta = self.client.get(reverse('seguimientoalumnoclase',kwargs={'alumnoid':1,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        #Probamos con un id alumno que no existe y redirige a inicio
        respuesta = self.client.get(reverse('seguimientoalumnoclase',kwargs={'alumnoid':4,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        
        respuesta = self.client.get(reverse('clases'), follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('alumnosclase',kwargs={'claseid':1,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('seguimientoclase',kwargs={'claseid':1,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('alumnos',kwargs={'alumno':1,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('alumnos'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('contenido'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('infoclase',kwargs={'claseid':1,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        #Estas pantallas son de Alumnos o usuarios sin registrar por lo que redirige al profesor a index
        respuesta = self.client.get(reverse('setEjercicios',kwargs={'idTema':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/setEjercicios.html')
        respuesta = self.client.post(reverse('index'),data={'tema':1})
        self.assertTemplateUsed(respuesta, 'divermat/setEjercicios.html')
        respuesta = self.client.get(reverse('examen',kwargs={'examen':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/examen.html')
        respuesta = self.client.get(reverse('videos'))
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('resumenes'))
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')
        respuesta = self.client.get(reverse('examenes'))
        self.assertTemplateUsed(respuesta, 'divermat/examenes.html')
        respuesta = self.client.get(reverse('cambiarInformacionAlumno'))
        self.assertTemplateUsed(respuesta, 'divermat/cambiarInformacionAlumno.html')
        #Esta pantalla cierra sesión y nos redirige al index por lo que se usa follow=True
        respuesta = self.client.get(reverse('cerrar_sesion'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')


class ViewsTestsWithProfesorLoggedIn(TestCase):
    """En esta clase vamos a probar el correcto funcionamiento de las vistas para un profesor loggeado"""
    @classmethod
    def setUpTestData(self):
        self.curso = Curso.objects.create(curso=1)
        self.curso2 = Curso.objects.create(curso=2)
        self.tema = Tema.objects.create(tema=1, curso=self.curso, titulo="Números Naturales")
        self.tema2 = Tema.objects.create(tema=3, curso=self.curso2, titulo="Ecuaciones")
        self.profesor = Profesor.objects.create(username="profe",first_name="Profesor", last_name="Prueba", tipo=0)
        self.ejercicio = Ejercicio.objects.create(curso=self.curso,tema=self.tema,titulo="Suma de números enteros",tipo=2,enunciado="¿Cuánto es 2+2?",soluciones="4",nsoluciones=1,solucion_correcta=4)
        self.ejercicio2 = Ejercicio.objects.create(curso=self.curso2,tema=self.tema2,titulo="Ecuaciones de primer grado",tipo=1,enunciado="¿Cuánto es x-2=2?",soluciones="2;4;3;5",nsoluciones=1,solucion_correcta=4)
        self.clase = Clase.objects.create(curso=self.curso,nombre="A",centro="IES Prueba",ano_academico=datetime.now(), n_alumnos=1,profesor=self.profesor)
        self.alumno = Alumno.objects.create(username="testAlumno",first_name="Alumno",last_name="Prueba",tipo=1, curso=self.curso, clase=self.clase, password="1234")
        self.alumno.save()
        self.alumno2 = Alumno.objects.create(username="testAlumno2",first_name="Alumno2",last_name="Prueba",tipo=1,password_temporal="1234", curso=self.curso, clase=self.clase)
        self.ejercicioUsuario = EjercicioUsuario.objects.create(ejercicio=self.ejercicio, alumno=self.alumno, soluciones_seleccionadas="4",resultado="¡Respuesta Correcta!")
        self.examen= Examen.objects.create(titulo="Examen tema 1", alumno=self.alumno,curso=self.curso,cronometrado=False,nota=100,inicio=datetime.now(timezone.utc))
        temas = []
        temas.append(self.tema.id)
        self.examen.temas.set(temas)
        ejerciciosAlumno = []
        ejerciciosAlumno.append(self.ejercicioUsuario.id)
        self.examen.ejercicios.set(ejerciciosAlumno)
        self.examen.save()
        self.seguimiento = Seguimiento.objects.create(alumno=self.alumno, tema=self.tema, n_ejercicios=1, acierto=100)
        ejercicios = []
        ejercicios.append(self.ejercicio.id)
        self.seguimiento.ejercicios.set(ejercicios)
        self.seguimiento.save()
        # self.video = Video.objects.create(curso=self.curso,tema=self.tema,titulo="Resolución de sumas de Números naturales",video=None)
        self.resumen = Resumen.objects.create(texto="........",curso=self.curso,tema=self.tema,titulo="Resolución de sumas de Números naturales")
        self.resumen = Resumen.objects.create(texto="........2",curso=self.curso2,tema=self.tema2,titulo="Resolución de ecuaciones de primer grado")
    
    def test_all_urls_are_correct_for_teachers(self):
        """Probamos que todas las urls que pueden ser accedidas
        por profesores dan 200 OK"""
        login = self.client.force_login(self.profesor)
        respuesta = self.client.get('/divermat/perfil/')
        self.assertEqual(respuesta.status_code, 200)
        #Redirige a la página de inicio
        respuesta = self.client.get('/divermat/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/index')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/Ejercicios')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/iniciar_sesion/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/registro/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/1/1/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/1/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejercicio/1/')
        self.assertEqual(respuesta.status_code, 200)
        # respuesta = self.client.get('/divermat/video/1/')
        # self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/resumen/1/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/clase/1',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/clase',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/cambiar_contrasenia/')
        self.assertEqual(respuesta.status_code, 200)
        #Estas pantallas son sólo del profesor
        respuesta = self.client.get('/divermat/alumnosclase/1/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/seguimientoclase/1/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/alumnos/1/')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/alumnos')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/contenido')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/seguimientoalumnoclase/1/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/clases')
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/infoclase/1/')
        self.assertEqual(respuesta.status_code, 200)
        #Estas pantallas son de Alumnos o usuarios sin registrar por lo que redirige al profesor a index
        respuesta = self.client.get('/divermat/Videos/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/videos/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/Resúmenes/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/resumenes/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/examenes/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/cambiarInformacionAlumno/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/setEjercicios/1/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/examen/1/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        #Esta pantalla cierra sesión y nos redirige al index por lo que se usa follow=True
        respuesta = self.client.get('/divermat/cerrar_sesion/',follow=True)
        self.assertEqual(respuesta.status_code, 200)

    def test_urls_when_wrong_param_for_teachers(self):
        """Probamos que todas las urls que pueden ser accedidas
        por profesores sin cuenta con un parametro con valor no válido o no existente dan 200 OK"""
        login = self.client.force_login(self.profesor)
        
        respuesta = self.client.get('/divermat/ejerciciosAsignados/a/1/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/1/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/a/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/10/1/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/1/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/10/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejerciciosAsignados/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejercicio/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/ejercicio/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        # respuesta = self.client.get('/divermat/video/1/',follow=True)
        # self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/resumen/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/resumen/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/clase/a',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/clase/10',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/alumnosclase/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/alumnosclase/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/seguimientoclase/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/seguimientoclase/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/alumnos/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/alumnos/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/seguimientoalumnoclase/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/seguimientoalumnoclase/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/infoclase/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/infoclase/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        #Estas pantallas son de Alumnos o usuarios sin registrar por lo que redirige al profesor a index
        respuesta = self.client.get('/divermat/setEjercicios/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/setEjercicios/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/examen/a/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get('/divermat/examen/10/',follow=True)
        self.assertEqual(respuesta.status_code, 200)
        self.client.logout()

    def test_all_urls_names_are_correct_for_teachers(self):
        """Probamos que todas las urls que pueden ser accedidas por
        profesores y son accedidas a través del nombre dan 200 OK"""
        login = self.client.force_login(self.profesor)
        respuesta = self.client.get(reverse('perfil'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('index'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('iniciar_sesion'),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('registro'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('ejerciciosAsignados',kwargs={'claseid':1,'ejercicioid':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('ejerciciosAsignados',kwargs={'claseid':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('ejerciciosAsignados'),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}))
        self.assertEqual(respuesta.status_code, 200)
        # respuesta = self.client.get(reverse('video',kwargs={'idVideo':1,}))
        # self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('resumen',kwargs={'idResumen':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('clase',kwargs={'clase':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('clase'),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('cambiar_contrasenia'))
        self.assertEqual(respuesta.status_code, 200)
        #Estas pantallas son del profesor por lo que nos redirige a index
        respuesta = self.client.get(reverse('seguimientoalumnoclase',kwargs={'alumnoid':1,}),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('clases'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('alumnosclase',kwargs={'claseid':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('seguimientoclase',kwargs={'claseid':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('alumnos',kwargs={'alumno':1,}))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('alumnos'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('contenido'))
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('infoclase',kwargs={'claseid':1,}))
        self.assertEqual(respuesta.status_code, 200)
        #Estas pantallas son de Alumnos o usuarios sin registrar por lo que redirige al profesor a index
        respuesta = self.client.get(reverse('setEjercicios',kwargs={'idTema':1,}),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('examen',kwargs={'examen':1,}),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('videos'),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('resumenes'),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('examenes'),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('cambiarInformacionAlumno'),follow=True)
        self.assertEqual(respuesta.status_code, 200)
        #Esta pantalla cierra sesión y nos redirige al index por lo que se usa follow=True
        respuesta = self.client.get(reverse('cerrar_sesion'),follow=True)
        self.assertEqual(respuesta.status_code, 200)

    def test_returned_templates_are_correct(self):
        """Probamos que las templates devueltas son las esperadas para un profesor
        y probamos los redirect en caso de que los argumentos pasados no sean correctos"""
        login = self.client.force_login(self.profesor)
        respuesta = self.client.get(reverse('perfil'))
        self.assertTemplateUsed(respuesta, 'divermat/perfil.html')
        respuesta = self.client.get(reverse('index'))
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosprof.html')
        respuesta = self.client.get(reverse('iniciar_sesion'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosprof.html')
        respuesta = self.client.get(reverse('registro'))
        self.assertTemplateUsed(respuesta, 'divermat/registro.html')
        respuesta = self.client.get(reverse('ejerciciosAsignados',kwargs={'claseid':1,'ejercicioid':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosAsignadosProfesor.html')
        respuesta = self.client.get(reverse('ejerciciosAsignados',kwargs={'claseid':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosAsignadosProfesor.html')
        respuesta = self.client.get(reverse('ejerciciosAsignados'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosprof.html')
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/ejercicioProfesor.html')
        #Probamos un ejercicio que no existe y debe redirigirnos al inicio
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':4,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosprof.html')
        # respuesta = self.client.get(reverse('video',kwargs={'idVideo':1,}))
        # self.assertEqual(respuesta.status_code, 200)
        respuesta = self.client.get(reverse('resumen',kwargs={'idResumen':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/resumen.html')
        #Probamos un resumen que no exitse y vacio y debe rediriginros la index
        respuesta = self.client.get(reverse('resumen',kwargs={'idResumen':3,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosprof.html')
        respuesta = self.client.get(reverse('clase',kwargs={'clase':1,}))
        self.assertTemplateUsed(respuesta, 'divermat/clase.html')
        #Probamos si no se indica el id de la clase
        respuesta = self.client.get(reverse('clase'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/clases.html')
        respuesta = self.client.get(reverse('cambiar_contrasenia'))
        self.assertTemplateUsed(respuesta, 'divermat/cambiocontrasenia.html')
        #Estas pantallas son del profesor  
        respuesta = self.client.get(reverse('seguimientoalumnoclase',kwargs={'alumnoid':2,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/seguimientoalumnoclase.html')
        
        #Probamos con un id alumno que no existe y redirige a inicio
        respuesta = self.client.get(reverse('seguimientoalumnoclase',kwargs={'alumnoid':4,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosprof.html')
        
        respuesta = self.client.get(reverse('clases'))
        self.assertTemplateUsed(respuesta, 'divermat/clases.html')
        respuesta = self.client.get(reverse('alumnosclase',kwargs={'claseid':1,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/alumnosclase.html')
        respuesta = self.client.get(reverse('seguimientoclase',kwargs={'claseid':1,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/seguimientoclase.html')
        respuesta = self.client.get(reverse('alumnos',kwargs={'alumno':1,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/alumnos.html')
        respuesta = self.client.get(reverse('alumnos'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/alumnos.html')
        respuesta = self.client.get(reverse('contenido'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/contenido.html')
        respuesta = self.client.get(reverse('infoclase',kwargs={'claseid':1,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/nuevainfoclase.html')
        #Estas pantallas son de Alumnos o usuarios sin registrar por lo que redirige al profesor a index
        respuesta = self.client.get(reverse('setEjercicios',kwargs={'idTema':1,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosprof.html')
        respuesta = self.client.get(reverse('examen',kwargs={'examen':1,}),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosprof.html')
        respuesta = self.client.get(reverse('videos'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosprof.html')
        respuesta = self.client.get(reverse('resumenes'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosprof.html')
        respuesta = self.client.get(reverse('examenes'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosprof.html')
        respuesta = self.client.get(reverse('cambiarInformacionAlumno'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/ejerciciosprof.html')
        #Esta pantalla cierra sesión y nos redirige al index por lo que se usa follow=True
        respuesta = self.client.get(reverse('cerrar_sesion'),follow=True)
        self.assertTemplateUsed(respuesta, 'divermat/inicio.html')


class ViewsContentSendToTemplate(TestCase):
    """En esta clase vamos a probar que las vistas devuelven la informacion correcta a las templates"""
    @classmethod
    def setUpTestData(self):
        self.curso = Curso.objects.create(curso=1)
        self.curso2 = Curso.objects.create(curso=2)
        self.tema = Tema.objects.create(tema=1, curso=self.curso, titulo="Números Naturales")
        self.tema2 = Tema.objects.create(tema=3, curso=self.curso2, titulo="Ecuaciones")
        self.profesor = Profesor.objects.create(username="profe",first_name="Profesor", last_name="Prueba", tipo=0,centro="IES Prueba")
        self.ejercicio = Ejercicio.objects.create(curso=self.curso,tema=self.tema,titulo="Suma de números enteros",tipo=2,enunciado="¿Cuánto es 2+2?",soluciones="4",nsoluciones=1,solucion_correcta=4)
        self.ejercicio2 = Ejercicio.objects.create(curso=self.curso2,tema=self.tema2,titulo="Ecuaciones de primer grado",tipo=1,enunciado="¿Cuánto es x-2=2?",soluciones="2;4;3;5",nsoluciones=1,solucion_correcta=4)
        self.clase = Clase.objects.create(curso=self.curso,nombre="A ciencias",centro="IES Prueba",ano_academico=datetime.now(), n_alumnos=1,profesor=self.profesor)
        self.clase2 = Clase.objects.create(curso=self.curso2,nombre="B",centro="IES Prueba",ano_academico=datetime.now(), n_alumnos=1,profesor=self.profesor)
        self.alumno = Alumno.objects.create(username="testAlumno",first_name="Alumno",last_name="Prueba",centro="IES Prueba",tipo=1, curso=self.curso, clase=self.clase, password="1234")
        self.alumno.save()
        self.alumno2 = Alumno.objects.create(username="testAlumno2",first_name="Alumno2",last_name="Prueba",centro="IES Prueba",tipo=1,password_temporal="1234", curso=self.curso2, clase=self.clase2)
        self.ejercicioUsuario = EjercicioUsuario.objects.create(ejercicio=self.ejercicio, alumno=self.alumno, soluciones_seleccionadas="4",resultado="¡Respuesta Correcta!")
        self.examen= Examen.objects.create(titulo="Examen de los temas, 1", alumno=self.alumno,curso=self.curso,cronometrado=False,nota=100,inicio=datetime.now(timezone.utc))
        temas = []
        temas.append(self.tema.id)
        self.examen.temas.set(temas)
        ejerciciosAlumno = []
        ejerciciosAlumno.append(self.ejercicioUsuario.id)
        self.examen.ejercicios.set(ejerciciosAlumno)
        self.examen.save()
        self.seguimiento = Seguimiento.objects.create(alumno=self.alumno, tema=self.tema, n_ejercicios=1, acierto=100)
        ejercicios = []
        ejercicios.append(self.ejercicio.id)
        self.seguimiento.ejercicios.set(ejercicios)
        self.seguimiento.save()
        # self.video = Video.objects.create(curso=self.curso,tema=self.tema,titulo="Resolución de sumas de Números naturales",video=None)
        self.resumen = Resumen.objects.create(texto="........",curso=self.curso,tema=self.tema,titulo="Resolución de sumas de Números naturales")
        self.resumen = Resumen.objects.create(texto="........2",curso=self.curso2,tema=self.tema2,titulo="Resolución de ecuaciones de primer grado")
        #Declaramos los diccionarios que se va a esperar encontrar en los contextos de respuesta de las peticiones
        self.EJERCICIO_DIC={'id': 1, 'curso': self.curso, 'titulo': 'Suma de números enteros'}
        self.EJERCICIO_DIC2={'id': 2, 'curso': self.curso2, 'titulo': 'Ecuaciones de primer grado'}
        self.RESUMEN_DIC={'id': 1, 'curso': self.curso, 'titulo': 'Resolución de sumas de Números naturales'}
        self.RESUMEN_DIC2={'id': 2, 'curso': self.curso2, 'titulo': 'Resolución de ecuaciones de primer grado'}
        self.SOLUCION_DATA={'solucion':'4','checked':False}
        self.SOLUCION_DATA_CHECKED={'solucion':'4','checked':True}
        self.SET_EJERCICIOS_DATA={'id': 1, 'enunciado': self.ejercicio.enunciado,'titulo':'Suma de números enteros','tipo':2,'nsoluciones':1,'foto':self.ejercicio.foto,'soluciones':[self.SOLUCION_DATA]}
        self.SET_EJERCICIOS_DATA_CHECKED={'id': 1, 'enunciado': self.ejercicio.enunciado,'titulo':'Suma de números enteros','tipo':2,'nsoluciones':1,'foto':self.ejercicio.foto,'soluciones':[self.SOLUCION_DATA_CHECKED],'resultado': '¡Respuesta Correcta!', 'solucion_introducida': '4'}
        self.EJERCICIO_EXAMEN={'id': 1, 'enunciado': self.ejercicio.enunciado,'titulo':'Suma de números enteros','tipo':2,'nsoluciones':1,'soluciones':[self.SOLUCION_DATA],'resultado': '¡Respuesta Correcta!', 'solucion_introducida': '4'}
        self.EJERCICIO_EXAMEN_CHECKED={'id': 1, 'enunciado': self.ejercicio.enunciado,'titulo':'Suma de números enteros','tipo':2,'nsoluciones':1,'soluciones':[self.SOLUCION_DATA_CHECKED],'resultado': '¡Respuesta Correcta!', 'solucion_introducida': '4'}
        self.EJERCICIO_EXAMEN_CHECKED_WRONG={'id': 1, 'enunciado': self.ejercicio.enunciado,'titulo':'Suma de números enteros','tipo':2,'nsoluciones':1,'soluciones':[self.SOLUCION_DATA_CHECKED],'resultado': 'Respuesta incorrecta el resultado esperado era 4', 'solucion_introducida': '4'}
        self.EXAMEN_DIC_CHECKED={'ejercicios': [self.EJERCICIO_EXAMEN_CHECKED], 'examen': self.examen}
        self.EXAMEN_DIC_CHECKED_WRONG={'ejercicios': [self.EJERCICIO_EXAMEN_CHECKED], 'examen': self.examen}
        self.RESUMEN_DIC={'id': 1, 'curso': self.curso, 'titulo': 'Resolución de sumas de Números naturales'}
        self.RESUMEN_DIC2={'id': 2, 'curso': self.curso2, 'titulo': 'Resolución de ecuaciones de primer grado'}
        self.INFORMACION_CLASE={'tema': '1 Números Naturales', 'acierto': 100.0, 'ejercicios': 1}
            
    def test_Index_context_is_correct(self):
        """Probamos el contenido enviado al Index por un usuario no loggeado"""
        tema1 = Tema.objects.all()[0]
        tema2 = Tema.objects.all()[1]
        respuesta = self.client.get(reverse('index'))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['ejercicios'])
        self.assertEqual(respuesta.context['Tipo'],'Ejercicios')
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        self.assertEqual(respuesta.context['Contenido'][0],self.EJERCICIO_DIC)
        self.assertEqual(respuesta.context['Contenido'][1],self.EJERCICIO_DIC2)
        self.assertEqual(len(respuesta.context['Contenido']),len(Ejercicio.objects.all()))
        
        """Probamos que el contenido es correcto si se aplica el filtro del curso"""
        respuesta = self.client.get(reverse('index'),{'curso':1})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['ejercicios'])
        self.assertEqual(respuesta.context['Tipo'],'Ejercicios')
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        self.assertEqual(respuesta.context['Contenido'][0],self.EJERCICIO_DIC)
        self.assertEqual(len(respuesta.context['Contenido']),len(Ejercicio.objects.filter(curso=self.curso)))

    
        """Probamos que el contenido es correcto si se aplica el filtro del tema"""
        respuesta = self.client.get(reverse('index'),{'tema':self.tema.titulo})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['ejercicios'])
        self.assertEqual(respuesta.context['Tipo'],'Ejercicios')
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        self.assertEqual(respuesta.context['Contenido'][0],self.EJERCICIO_DIC)
        self.assertEqual(len(respuesta.context['Contenido']),len(Ejercicio.objects.filter(tema=self.tema)))

        """Probamos que el contenido es correcto si se aplica la búsqueda"""
        respuesta = self.client.get(reverse('index'),{'buscar':'Ecuac'})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['ejercicios'])
        self.assertEqual(respuesta.context['Tipo'],'Ejercicios')
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        self.assertEqual(respuesta.context['Contenido'][0],self.EJERCICIO_DIC2)
        self.assertEqual(len(respuesta.context['Contenido']),1)
    
    def test_Index_context_is_correct_Alumno(self):
        """Probamos el contenido enviado al Index por un alumno"""
        login = self.client.force_login(self.alumno)
        respuesta = self.client.get(reverse('index'))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['ejercicios'])
        self.assertEqual(respuesta.context['Tipo'],'Ejercicios')
        self.assertEqual(respuesta.context['clase'],self.alumno.clase)
        self.assertEqual(respuesta.context['usuario'],self.alumno.username)
        self.assertEqual(respuesta.context['temas'][0],Tema.objects.filter(curso=self.alumno.curso)[0].titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.filter(curso=self.alumno.curso)))
        self.assertEqual(respuesta.context['Contenido'][0],self.EJERCICIO_DIC)
        self.assertEqual(len(respuesta.context['Contenido']),len(Ejercicio.objects.filter(curso=self.alumno.curso)))
    
        self.client.logout()
    
    def test_Index_context_is_correct_Profesor(self):
        """Probamos el contenido enviado al Index por un profesor"""
        tema1 = Tema.objects.all()[0]
        login = self.client.force_login(self.profesor)
        respuesta = self.client.get(reverse('index'))
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['ejercicios'])
        self.assertEqual(respuesta.context['Tipo'],'Ejercicios')
        self.assertEqual(respuesta.context['clases'][0],Clase.objects.filter(profesor=self.profesor)[0])
        self.assertEqual(len(respuesta.context['clases']),len(Clase.objects.filter(profesor=self.profesor)))
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        self.assertEqual(respuesta.context['Contenido'][0],self.EJERCICIO_DIC)
        self.assertEqual(respuesta.context['Contenido'][1],self.EJERCICIO_DIC2)
        self.assertEqual(len(respuesta.context['Contenido']),len(Ejercicio.objects.all()))
    
        self.client.logout() 

    def test_Inicio_sesion_context_is_correct(self):
        """Probamos el contenido enviado a Inicio de Sesion por un usuario no loggeado"""
        respuesta = self.client.get(reverse('iniciar_sesion'))
        self.assertEqual(str(respuesta.context['form']),str(InicioSesion()))
        self.client.logout()

    def test_Perfil_context_is_correct_Alumno(self):
        """Probamos el contenido enviado al Perfil por un alumno"""
        login = self.client.force_login(self.alumno)
        respuesta = self.client.get(reverse('perfil'))
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['clase'],self.alumno.clase)
        self.assertEqual(len(respuesta.context['seguimiento']),len(Seguimiento.objects.filter(alumno=self.alumno)))
        self.assertEqual(respuesta.context['seguimiento'][0],Seguimiento.objects.filter(alumno=self.alumno)[0])

        self.client.logout()
    
    def test_Perfil_context_is_correct_Profesor(self):
        """Probamos el contenido enviado al Perfil por un profesor"""
        login = self.client.force_login(self.profesor)
        respuesta = self.client.get(reverse('perfil'))
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['nombre'],self.profesor.first_name)
        self.assertEqual(respuesta.context['apellidos'],self.profesor.last_name)
        self.assertEqual(respuesta.context['username'],self.profesor.username)
        self.assertEqual(respuesta.context['centro'],self.profesor.centro)
        """Probamos la llamada post para actualizar el username"""
        respuesta = self.client.post(reverse('perfil'), data={'username': 'Updated'}, follow=True)
        self.profesor = Profesor.objects.get(id=self.profesor.id)
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['nombre'],self.profesor.first_name)
        self.assertEqual(respuesta.context['username'],"Updated")
        self.assertEqual(respuesta.context['apellidos'],self.profesor.last_name)
        self.assertEqual(respuesta.context['username'],self.profesor.username)
        self.assertEqual(respuesta.context['centro'],self.profesor.centro)
        """Probamos la llamada post para actualizar el centro"""
        respuesta = self.client.post(reverse('perfil'), data={'centro': 'Updated'}, follow=True)
        self.profesor = Profesor.objects.get(id=self.profesor.id)
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['nombre'],self.profesor.first_name)
        self.assertEqual(respuesta.context['centro'],"Updated")
        self.assertEqual(respuesta.context['apellidos'],self.profesor.last_name)
        self.assertEqual(respuesta.context['username'],self.profesor.username)
        self.assertEqual(respuesta.context['centro'],self.profesor.centro)

        self.client.logout()
    
    def test_CambiarInformacionAlumno_context_is_correct_Alumno(self):
        """Probamos el contenido enviado a Cambiar Informacion Alumno por un alumno"""
        login = self.client.force_login(self.alumno)
        respuesta = self.client.get(reverse('cambiarInformacionAlumno'))
        self.assertFalse(respuesta.context['registro'])
        self.assertEqual(respuesta.context['nombre'],self.alumno.first_name)
        self.assertEqual(respuesta.context['apellidos'],self.alumno.last_name)
        self.assertEqual(respuesta.context['username'],self.alumno.username)
        self.assertEqual(respuesta.context['centro'],self.alumno.centro)
        """Probamos la llamada POST para actualizar el nombre"""
        respuesta = self.client.post(reverse('cambiarInformacionAlumno'), data={'first_name': 'Updated'}, follow=True)
        self.alumno = Alumno.objects.get(id=self.alumno.id)
        self.assertFalse(respuesta.context['registro'])
        self.assertEqual(respuesta.context['nombre'],self.alumno.first_name)
        self.assertEqual(respuesta.context['nombre'],"Updated")
        self.assertEqual(respuesta.context['apellidos'],self.alumno.last_name)
        self.assertEqual(respuesta.context['username'],self.alumno.username)
        self.assertEqual(respuesta.context['centro'],self.alumno.centro)
        """Probamos la llamada POST para actualizar el apellido"""
        respuesta = self.client.post(reverse('cambiarInformacionAlumno'), data={'last_name': 'Updated'}, follow=True)
        self.alumno = Alumno.objects.get(id=self.alumno.id)
        self.assertFalse(respuesta.context['registro'])
        self.assertEqual(respuesta.context['nombre'],self.alumno.first_name)
        self.assertEqual(respuesta.context['apellidos'],self.alumno.last_name)
        self.assertEqual(respuesta.context['apellidos'],"Updated")
        self.assertEqual(respuesta.context['username'],self.alumno.username)
        self.assertEqual(respuesta.context['centro'],self.alumno.centro)
        
        self.client.logout()
    
    def test_SetEjercicios_context_is_correct_Alumno(self):
        """Probamos el contenido enviado a Set Ejercicios por un alumno"""
        login = self.client.force_login(self.alumno)
        respuesta = self.client.get(reverse('setEjercicios',kwargs={'idTema':1,}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['tema'],self.tema)
        self.assertEqual(len(respuesta.context['set']),1)
        self.assertEqual(respuesta.context['set'][0],self.SET_EJERCICIOS_DATA)
        
        """Probamos la llamada POST para recibir un nuevo Set"""
        respuesta = self.client.post(reverse('setEjercicios',kwargs={'idTema':1,}),data={'1':'4'})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['tema'],self.tema)
        self.assertEqual(len(respuesta.context['set']),1)
        self.assertEqual(respuesta.context['set'][0],self.SET_EJERCICIOS_DATA_CHECKED)
        
        self.client.logout()
    
    def test_examenes_context_is_correct(self):
        """Probamos el contenido enviado a Examenes por un usuario no loggeado"""
        respuesta=self.client.get(reverse('examenes'))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertFalse(respuesta.context['examen'])

        form = NuevoExamen(curso=None)
        self.assertEqual(str(respuesta.context['form']),str(form))
        
        """Probamos la petición GET con filtro de curso"""
        respuesta=self.client.get(reverse('examenes'),data={"curso":self.curso,})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertFalse(respuesta.context['examen'])

        form = NuevoExamen(curso=self.curso)
        self.assertEqual(str(respuesta.context['form']),str(form))

        """Probamos la petición POST que genera un nuevo examen"""
        self.examen.id=2
        self.EXAMEN_NUEVO_DIC={'examen': self.examen,'ejercicios': [self.SET_EJERCICIOS_DATA]}
        respuesta=self.client.post(reverse('examenes'),data={"temas":[self.tema.id],"crono":True,})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['examen'])
        self.assertTrue(respuesta.context['hacer_examen'])
        self.assertEqual(respuesta.context['n_examen'],1)
        self.assertEqual(respuesta.context['examen_data'],self.EXAMEN_NUEVO_DIC)

    def test_examenes_context_is_correct_Alumno(self):
        """Probamos el contenido enviado a Examenes por un alumno"""
        login=self.client.force_login(self.alumno)
        respuesta=self.client.get(reverse('examenes'))
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertFalse(respuesta.context['examen'])

        form = NuevoExamen(curso=self.alumno.curso)
        self.assertEqual(str(respuesta.context['form']),str(form))
        
        """Probamos la petición POST que genera un nuevo examen"""
        self.examen.id=2
        self.EXAMEN_NUEVO_DIC={'examen': self.examen,'ejercicios': [self.SET_EJERCICIOS_DATA]}
        respuesta=self.client.post(reverse('examenes'),data={"temas":[self.tema.id],"crono":True,})
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['examen'])
        self.assertTrue(respuesta.context['hacer_examen'])
        self.assertEqual(respuesta.context['n_examen'],1)
        self.assertEqual(respuesta.context['examen_data'],self.EXAMEN_NUEVO_DIC)

        self.client.logout()
    
    def test_examen_context_is_correct(self):
        """Probamos el contenido enviado a Examen por un usuario no loggeado"""
        respuesta=self.client.get(reverse('examen', kwargs={'examen':1,}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['nota'])
        self.assertFalse(respuesta.context['hacer_examen'])
        self.assertEqual(respuesta.context['examen_data'],self.EXAMEN_DIC_CHECKED)

        """Probamos cuando la petición es de tipo POST y se envia la solucion al examen actual exitosa"""
        respuesta=self.client.post(reverse('examen', kwargs={'examen':1,}),data={'1':4})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['nota'])
        self.assertFalse(respuesta.context['hacer_examen'])
        self.assertEqual(respuesta.context['examen_data'],self.EXAMEN_DIC_CHECKED)
        
        """Probamos cuando la petición es de tipo POST y se envia la solucion al examen actual erronea"""
        respuesta=self.client.post(reverse('examen', kwargs={'examen':1,}),data={'1':3})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['nota'])
        self.assertFalse(respuesta.context['hacer_examen'])
        self.assertEqual(respuesta.context['examen_data'],self.EXAMEN_DIC_CHECKED_WRONG)

    def test_examen_context_is_correct_Alumno(self):
        """Probamos el contenido enviado a Examen por un alumno"""
        login=self.client.force_login(self.alumno)
        respuesta=self.client.get(reverse('examen', kwargs={'examen':1,}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['nota'])
        self.assertFalse(respuesta.context['hacer_examen'])
        self.assertEqual(respuesta.context['examen_data'],self.EXAMEN_DIC_CHECKED)  
        
        """Probamos cuando la petición es de tipo POST y se envia la solucion al examen actual exitosa"""
        respuesta=self.client.post(reverse('examen', kwargs={'examen':1,}),data={'1':4})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['nota'])
        self.assertFalse(respuesta.context['hacer_examen'])
        self.assertEqual(respuesta.context['examen_data'],self.EXAMEN_DIC_CHECKED)
        
        """Probamos cuando la petición es de tipo POST y se envia la solucion al examen actual erronea"""
        respuesta=self.client.post(reverse('examen', kwargs={'examen':1,}),data={'1':3})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['nota'])
        self.assertFalse(respuesta.context['hacer_examen'])
        self.assertEqual(respuesta.context['examen_data'],self.EXAMEN_DIC_CHECKED_WRONG)
        self.client.logout()

    def test_Videos_context_is_correct(self):
        """Probamos el contenido enviado a Videos por un usuario no loggeado"""
        tema1 = Tema.objects.all()[0]
        tema2 = Tema.objects.all()[1]
        respuesta = self.client.get(reverse('videos'))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['Tipo'],'Videos')
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        # self.assertEqual(respuesta.context['Contenido'][0],self.VIDEO_DIC)
        # self.assertEqual(respuesta.context['Contenido'][1],self.VIDEO_DIC2)
        self.assertEqual(len(respuesta.context['Contenido']),len(Video.objects.all()))
        
        """Probamos que el contenido es correcto si se aplica el filtro del curso"""
        respuesta = self.client.get(reverse('videos'),{'curso':1})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['Tipo'],'Videos')
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        # self.assertEqual(respuesta.context['Contenido'][0],self.RESUMEN_DIC)
        self.assertEqual(len(respuesta.context['Contenido']),len(Video.objects.filter(curso=self.curso)))

    
        """Probamos que el contenido es correcto si se aplica el filtro del tema"""
        respuesta = self.client.get(reverse('videos'),{'tema':self.tema.titulo})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['Tipo'],'Videos')
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        # self.assertEqual(respuesta.context['Contenido'][0],self.RESUMEN_DIC)
        self.assertEqual(len(respuesta.context['Contenido']),len(Video.objects.filter(tema=self.tema)))


        """Probamos que el contenido es correcto si se aplica la búsqueda"""
        respuesta = self.client.get(reverse('videos'),{'buscar':'Ecuac'})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['Tipo'],'Videos')
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        # self.assertEqual(respuesta.context['Contenido'][0],self.RESUMEN_DIC2)
        # self.assertEqual(len(respuesta.context['Contenido']),1)
    
    def test_Videos_context_is_correct_Alumno(self):
        """Probamos el contenido enviado a Videos por un alumno"""
        login=self.client.force_login(user=self.alumno)
        respuesta = self.client.get(reverse('videos'))
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['Tipo'],'Videos')
        self.assertEqual(respuesta.context['temas'][0],Tema.objects.filter(curso=self.alumno.curso)[0].titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.filter(curso=self.alumno.curso)))
        # self.assertEqual(respuesta.context['Contenido'][0],self.RESUMEN_DIC)
        self.assertEqual(len(respuesta.context['Contenido']),len(Video.objects.filter(curso=self.alumno.curso)))
        self.client.logout()

    def test_Resumenes_context_is_correct(self):
        """Probamos el contenido enviado a Resumenes por un usuario no loggeado"""
        tema1 = Tema.objects.all()[0]
        tema2 = Tema.objects.all()[1]
        respuesta = self.client.get(reverse('resumenes'))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['Tipo'],'Resúmenes')
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        self.assertEqual(respuesta.context['Contenido'][0],self.RESUMEN_DIC)
        self.assertEqual(respuesta.context['Contenido'][1],self.RESUMEN_DIC2)
        self.assertEqual(len(respuesta.context['Contenido']),len(Resumen.objects.all()))
        
        """Probamos que el contenido es correcto si se aplica el filtro del curso"""
        respuesta = self.client.get(reverse('resumenes'),{'curso':1})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['Tipo'],'Resúmenes')
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        self.assertEqual(respuesta.context['Contenido'][0],self.RESUMEN_DIC)
        self.assertEqual(len(respuesta.context['Contenido']),len(Resumen.objects.filter(curso=self.curso)))

    
        """Probamos que el contenido es correcto si se aplica el filtro del tema"""
        respuesta = self.client.get(reverse('resumenes'),{'tema':self.tema.titulo})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['Tipo'],'Resúmenes')
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        self.assertEqual(respuesta.context['Contenido'][0],self.RESUMEN_DIC)
        self.assertEqual(len(respuesta.context['Contenido']),len(Resumen.objects.filter(tema=self.tema)))


        """Probamos que el contenido es correcto si se aplica la búsqueda"""
        respuesta = self.client.get(reverse('resumenes'),{'buscar':'Ecuac'})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['Tipo'],'Resúmenes')
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        self.assertEqual(respuesta.context['Contenido'][0],self.RESUMEN_DIC2)
        self.assertEqual(len(respuesta.context['Contenido']),1)
    
    def test_Resumenes_context_is_correct_Alumno(self):
        """"Probamos el contenido enviado a Resumenes por un alumno"""
        login=self.client.force_login(user=self.alumno)
        respuesta = self.client.get(reverse('resumenes'))
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['Tipo'],'Resúmenes')
        self.assertEqual(respuesta.context['temas'][0],Tema.objects.filter(curso=self.alumno.curso)[0].titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.filter(curso=self.alumno.curso)))
        self.assertEqual(respuesta.context['Contenido'][0],self.RESUMEN_DIC)
        self.assertEqual(len(respuesta.context['Contenido']),len(Resumen.objects.filter(curso=self.alumno.curso)))
        self.client.logout()
        
    def test_Resumen_context_is_correct(self):
        """Probamos el contenido enviado al Resumen por un usuario no loggeado"""
        respuesta = self.client.get(reverse('resumen',kwargs={'idResumen':1,}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['resumen'],Resumen.objects.get(id=1))
    
    def test_Resumen_context_is_correct_Alumno(self):
        """Probamos el contenido enviado a Resumen por un alumno"""
        login=self.client.force_login(self.alumno)
        respuesta = self.client.get(reverse('resumen',kwargs={'idResumen':1,}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['resumen'],Resumen.objects.get(id=1))
        self.client.logout()
    
    def test_Resumen_context_is_correct_Profesor(self):
        """Probamos el contenido enviado a Resumen por un profesor"""
        login=self.client.force_login(self.profesor)
        respuesta = self.client.get(reverse('resumen',kwargs={'idResumen':1,}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['resumen'],Resumen.objects.get(id=1))
        self.client.logout()
    
    def test_Ejercicio_context_is_correct(self):
        """Probamos el contenido enviado al Ejercicio por un usuario no loggeado"""
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['ejercicio'],self.ejercicio)
        self.assertEqual(len(respuesta.context['soluciones']),1)
        self.assertEqual(respuesta.context['soluciones'][0],self.SOLUCION_DATA)
        self.assertEqual(respuesta.context['solucion_introducida'],'')

        """Probamos el contenido en caso de que la petición tuviese el ejercicio resuelto correctamente"""
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}),data={'solucion':'4'})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['ejercicio'],self.ejercicio)
        self.assertEqual(len(respuesta.context['soluciones']),1)
        self.assertEqual(respuesta.context['soluciones'][0],self.SOLUCION_DATA_CHECKED)
        self.assertEqual(respuesta.context['solucion_introducida'],'4')
        self.assertEqual(respuesta.context['resultado'],"¡Respuesta correcta!")
        
        """Probamos el contenido en caso de que la petición tuviese el ejercicio resuelto incorrectamente"""
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}),data={'solucion':'3'})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['ejercicio'],self.ejercicio)
        self.assertEqual(len(respuesta.context['soluciones']),1)
        self.assertEqual(respuesta.context['soluciones'][0],self.SOLUCION_DATA)
        self.assertEqual(respuesta.context['solucion_introducida'],'3')
        self.assertEqual(respuesta.context['resultado'],"Respuesta incorrecta, el resultado esperado era: 4")

    def test_Ejercicio_context_is_correct_Alumno(self):
        """Probamos el contenido enviado a Ejercicio por un alumno"""
        login=self.client.force_login(self.alumno)
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['ejercicio'],self.ejercicio)
        self.assertEqual(len(respuesta.context['soluciones']),1)
        self.assertEqual(respuesta.context['soluciones'][0],self.SOLUCION_DATA)
        self.assertEqual(respuesta.context['solucion_introducida'],'')

        """Probamos el contenido en caso de que la petición tuviese el ejercicio resuelto correctamente"""
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}),data={'solucion':'4'})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['ejercicio'],self.ejercicio)
        self.assertEqual(len(respuesta.context['soluciones']),1)
        self.assertEqual(respuesta.context['soluciones'][0],self.SOLUCION_DATA_CHECKED)
        self.assertEqual(respuesta.context['solucion_introducida'],'4')
        self.assertEqual(respuesta.context['resultado'],"¡Respuesta correcta!")
        
        """Probamos el contenido en caso de que la petición tuviese el ejercicio resuelto incorrectamente"""
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}),data={'solucion':'3'})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['ejercicio'],self.ejercicio)
        self.assertEqual(len(respuesta.context['soluciones']),1)
        self.assertEqual(respuesta.context['soluciones'][0],self.SOLUCION_DATA)
        self.assertEqual(respuesta.context['solucion_introducida'],'3')
        self.assertEqual(respuesta.context['resultado'],"Respuesta incorrecta, el resultado esperado era: 4")
        self.client.logout()
    
    def test_Ejercicio_context_is_correct_Profesor(self):
        """Probamos el contenido enviado a Ejercicio por un profesor"""
        login=self.client.force_login(self.profesor)
        respuesta = self.client.get(reverse('ejercicio',kwargs={'ejercicio':1,}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['ejercicio'],self.ejercicio)
        self.assertEqual(len(respuesta.context['soluciones']),1)
        self.assertEqual(respuesta.context['soluciones'][0],self.SOLUCION_DATA_CHECKED)
        self.client.logout()
    
    def test_Clases_context_is_correct_Profesor(self):
        """Probamos el contenido enviado a Clases por un alumno"""
        login=self.client.force_login(user=self.profesor)
        respuesta = self.client.get(reverse('clases'))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['clases'][0],Clase.objects.filter(profesor=self.profesor)[0])
        self.assertEqual(respuesta.context['clases'][1],Clase.objects.filter(profesor=self.profesor)[1])
        self.assertEqual(len(respuesta.context['clases']),len(Clase.objects.filter(profesor=self.profesor)))
        self.assertEqual(str(respuesta.context['form']),str(NuevaClase()))
        
        """Probamos GET pero con parámetros en la búsqueda"""
        respuesta = self.client.get(reverse('clases'),data={"buscar":"A cienc"})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['clases'][0],Clase.objects.filter(profesor=self.profesor)[0])
        self.assertEqual(len(respuesta.context['clases']),1)
        self.assertEqual(str(respuesta.context['form']),str(NuevaClase()))

        """Probamos GET pero con el filtro del curso"""
        respuesta = self.client.get(reverse('clases'),data={"curso":"2º ESO"})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['clases'][0],Clase.objects.filter(profesor=self.profesor)[1])
        self.assertEqual(len(respuesta.context['clases']),1)
        self.assertEqual(str(respuesta.context['form']),str(NuevaClase()))

        """Probamos POST para la creación de una clase y sus alumnos"""
        respuesta = self.client.post(reverse('clases'),data={"nombre":"C",'curso':2,'n_alumnos':1,'ano_academico':"2023-03-22"})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['clases'][0],Clase.objects.filter(profesor=self.profesor)[0])
        self.assertEqual(respuesta.context['clases'][1],Clase.objects.filter(profesor=self.profesor)[1])
        self.assertEqual(respuesta.context['clases'][2],Clase.objects.filter(profesor=self.profesor)[2])
        self.assertEqual(len(respuesta.context['clases']),3)
        self.assertEqual(str(respuesta.context['form']),str(NuevaClase()))
        # Tenemos los dos alumnos creados en el setUp más el generado con la clase
        self.assertEqual(len(Alumno.objects.all()),3)

        self.client.logout()
    
    def test_Alumnos_context_is_correct_Profesor(self):
        """Probamos el contenido enviado a Alumnos por un profesor"""
        login=self.client.force_login(user=self.profesor)
        #Alumnos del profesor
        alumnos = []
        for clase in Clase.objects.filter(profesor=self.profesor):
            alumnos_clase = Alumno.objects.filter(clase=clase)
            for alumno_indv in alumnos_clase:
                alumnos.append(alumno_indv)

        respuesta = self.client.get(reverse('alumnos'))
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['alumnos'][0],alumnos[0])
        self.assertEqual(respuesta.context['alumnos'][1],alumnos[1])
        self.assertEqual(len(respuesta.context['alumnos']),2)
        self.assertFalse(respuesta.context['seguimiento'])
        """Probamos GET pero con parámetros en la búsqueda"""
        respuesta = self.client.get(reverse('alumnos'),data={"buscar":"testAlumno2"})
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['alumnos'][0],alumnos[1])
        self.assertEqual(len(respuesta.context['alumnos']),1)
        self.assertFalse(respuesta.context['seguimiento'])

        """Probamos GET pero con el filtro del curso"""
        respuesta = self.client.get(reverse('alumnos'),data={"curso":"1º ESO"})
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['alumnos'][0],alumnos[0])
        self.assertEqual(len(respuesta.context['alumnos']),1)
        self.assertFalse(respuesta.context['seguimiento'])


        """Probamos GET con el parametro alumno para mostrar el seguimiento de este"""
        respuesta = self.client.get(reverse('alumnos',kwargs={'alumno':2}))
        self.assertFalse(respuesta.context['registro'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['alumnos'][0],alumnos[0])
        self.assertEqual(respuesta.context['alumnos'][1],alumnos[1])
        self.assertEqual(len(respuesta.context['alumnos']),2)
        self.assertTrue(respuesta.context['seguimiento'])
        self.assertEqual(respuesta.context['alumno'],alumnos[0])
        self.assertEqual(len(respuesta.context['informacion']),len(Seguimiento.objects.filter(alumno=alumnos[0])))
        self.assertEqual(respuesta.context['informacion'][0],Seguimiento.objects.filter(alumno=alumnos[0])[0])

        self.client.logout()
    
    def test_Contenido_context_is_correct_Profesor(self):
        """Probamos el contenido enviado a Contenido por un profesor"""
        tema1 = Tema.objects.all()[0]
        tema2 = Tema.objects.all()[1]
        login=self.client.force_login(user=self.profesor)
        respuesta = self.client.get(reverse('contenido'))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        # self.assertEqual(respuesta.context['videos'][0],Video.objects.all()[0])
        # self.assertEqual(len(respuesta.context['videos']),len(Video.objects.all()))
        self.assertEqual(respuesta.context['resumenes'][0],self.RESUMEN_DIC)
        self.assertEqual(respuesta.context['resumenes'][1],self.RESUMEN_DIC2)
        self.assertEqual(len(respuesta.context['resumenes']),len(Resumen.objects.all()))
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        
        """Probamos que el contenido es correcto si se aplica el filtro del curso"""
        respuesta = self.client.get(reverse('contenido'),{'curso':1})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        # self.assertEqual(respuesta.context['videos'][0],Video.objects.filter(curso=self.curso)[0])
        # self.assertEqual(len(respuesta.context['videos']),len(Video.objects.filter(curso=self.curso)))
        self.assertEqual(respuesta.context['resumenes'][0],self.RESUMEN_DIC)
        self.assertEqual(len(respuesta.context['resumenes']),len(Resumen.objects.filter(curso=self.curso)))
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
    
        """Probamos que el contenido es correcto si se aplica el filtro del tema"""
        respuesta = self.client.get(reverse('contenido'),{'tema':self.tema.titulo})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        # self.assertEqual(respuesta.context['videos'][0],Video.objects.filter(tema=self.tema)[0])
        # self.assertEqual(len(respuesta.context['videos']),len(Video.objects.filter(tema=self.tema)))
        self.assertEqual(respuesta.context['resumenes'][0],self.RESUMEN_DIC)
        self.assertEqual(len(respuesta.context['resumenes']),len(Resumen.objects.filter(tema=self.tema)))
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))

        """Probamos que el contenido es correcto si se aplica la búsqueda"""
        respuesta = self.client.get(reverse('contenido'),{'buscar':'Ecuac'})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        # self.assertEqual(respuesta.context['videos'][0],Video.objects.all()[0])
        # self.assertEqual(len(respuesta.context['videos']),len(Video.objects.all()))
        self.assertEqual(respuesta.context['resumenes'][0],self.RESUMEN_DIC2)
        self.assertEqual(len(respuesta.context['resumenes']),1)
        self.assertEqual(respuesta.context['temas'][0],str(tema1.curso)+"º."+tema1.titulo)
        self.assertEqual(respuesta.context['temas'][1],str(tema2.curso)+"º."+tema2.titulo)
        self.assertEqual(len(respuesta.context['temas']),len(Tema.objects.all()))
        

        self.client.logout()
    
    def test_Clase_context_is_correct_Alumno(self):
        """Probamos el contenido enviado a Clase por un alumno"""
        login=self.client.force_login(user=self.alumno)
        respuesta = self.client.get(reverse('clase',kwargs={'clase':1}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['clase'],self.clase)
        self.assertEqual(respuesta.context['curso'],self.clase.curso)
        self.assertEqual(respuesta.context['nombre'],self.clase.nombre)
        self.assertEqual(respuesta.context['ano_academico'].year,self.clase.ano_academico.year)
        self.assertEqual(respuesta.context['ano_academico'].day,self.clase.ano_academico.day)
        self.assertEqual(respuesta.context['ano_academico'].month,self.clase.ano_academico.month)
        self.assertEqual(respuesta.context['nalumnos'],self.clase.n_alumnos)
        self.assertEqual(respuesta.context['centro'],self.clase.centro)

        self.client.logout()

    def test_Clase_context_is_correct_Profesor(self):
        """Probamos el contenido enviado al Clase por un profesor"""
        login=self.client.force_login(user=self.profesor)
        respuesta = self.client.get(reverse('clase',kwargs={'clase':self.clase.id}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['clase'],self.clase)
        self.assertEqual(respuesta.context['curso'],self.clase.curso)
        self.assertEqual(respuesta.context['nombre'],self.clase.nombre)
        self.assertEqual(respuesta.context['ano_academico'].year,self.clase.ano_academico.year)
        self.assertEqual(respuesta.context['ano_academico'].day,self.clase.ano_academico.day)
        self.assertEqual(respuesta.context['ano_academico'].month,self.clase.ano_academico.month)
        self.assertEqual(respuesta.context['nalumnos'],self.clase.n_alumnos)
        self.assertEqual(respuesta.context['centro'],self.clase.centro)
        self.assertEqual(len(respuesta.context['alumnos']),self.clase.n_alumnos)
        self.assertEqual(respuesta.context['alumnos'][0],self.alumno)
        self.assertEqual(len(respuesta.context['informacion']),1)
        self.assertEqual(respuesta.context['informacion'][0],self.INFORMACION_CLASE)

        self.client.logout()

    def test_InfoClase_context_is_correct_Profesor(self):
        """Probamos el contenido enviado a infoClase por un profesor"""
        login=self.client.force_login(user=self.profesor)
        respuesta = self.client.get(reverse('infoclase',kwargs={'claseid':self.clase.id}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['clase'],self.clase)
        self.assertEqual(respuesta.context['curso'],self.clase.curso)
        self.assertEqual(respuesta.context['nombre'],self.clase.nombre)
        self.assertEqual(respuesta.context['ano_academico'].year,self.clase.ano_academico.year)
        self.assertEqual(respuesta.context['ano_academico'].day,self.clase.ano_academico.day)
        self.assertEqual(respuesta.context['ano_academico'].month,self.clase.ano_academico.month)
        self.assertEqual(respuesta.context['centro'],self.clase.centro)
        self.assertEqual(str(respuesta.context['form']),str(NuevaInfoClase()))
        
        """Probamos POST para actualizar la información"""
        respuesta = self.client.post(reverse('infoclase',kwargs={'claseid':self.clase.id}),data={'nombre':'Updated','centro':'Updated','ano_academico':"2010-05-12",'curso':2})
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['clase'],self.clase)
        self.assertEqual(respuesta.context['curso'],self.curso2)
        self.assertEqual(respuesta.context['nombre'],"Updated")
        self.assertEqual(respuesta.context['ano_academico'].year,2010)
        self.assertEqual(respuesta.context['ano_academico'].day,12)
        self.assertEqual(respuesta.context['ano_academico'].month, 5)
        self.assertEqual(respuesta.context['centro'],"Updated")

        self.client.logout()

    def test_SeguimientoClase_context_is_correct_Profesor(self):
        """Probamos el contenido enviado a seguimientoClase por un profesor"""
        login=self.client.force_login(user=self.profesor)
        self.clase.ejercicios.add(self.ejercicio)
        self.clase.save()
        respuesta = self.client.get(reverse('seguimientoclase',kwargs={'claseid':self.clase.id}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['clase'],self.clase)
        self.assertEqual(len(respuesta.context['informacion']),1)
        self.assertEqual(respuesta.context['informacion'][0],self.INFORMACION_CLASE)
        self.assertEqual(respuesta.context['ejercicios_asignados'][0],self.clase.ejercicios.all()[0])
        self.assertEqual(len(respuesta.context['ejercicios_asignados']),len(self.clase.ejercicios.all()))
        self.client.logout()
    

    def test_SeguimientoAlumnoClase_context_is_correct_Profesor(self):
        """Probamos el contenido enviado a seguimientoAlumnoClase por un profesor"""
        login = self.client.force_login(self.profesor)
        respuesta = self.client.get(reverse('seguimientoalumnoclase',kwargs={'alumnoid':self.alumno.id}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['nombre'],self.alumno.first_name)
        self.assertEqual(respuesta.context['apellidos'],self.alumno.last_name)
        self.assertEqual(respuesta.context['username'],self.alumno.username)
        self.assertEqual(respuesta.context['centro'],self.alumno.centro)
        self.assertEqual(respuesta.context['clase'],self.alumno.clase)
        self.assertEqual(len(respuesta.context['seguimiento']),len(Seguimiento.objects.filter(alumno=self.alumno)))
        self.assertEqual(respuesta.context['seguimiento'][0],Seguimiento.objects.filter(alumno=self.alumno)[0])

        self.client.logout()
    
    def test_EjerciciosAsignados_context_is_correct_Alumno(self):
        """Probamos el contenido enviado a Ejercicios Asignados por un alumno"""
        login = self.client.force_login(user=self.alumno)
        ejercicio_asignado = Ejercicio.objects.create(curso=self.curso,tema=self.tema,titulo="Resta de números enteros",tipo=1,enunciado="¿Cuánto es 2-2?",soluciones="0;4;-4;-2",nsoluciones=1,solucion_correcta=0)
        self.clase.ejercicios.add(ejercicio_asignado)
        self.clase.ejercicios.add(self.ejercicio)
        self.clase.save()
        respuesta = self.client.get(reverse('ejerciciosAsignados'))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['profesor'])
        self.assertTrue(respuesta.context['alumno'])
        self.assertEqual(respuesta.context['clase'],self.alumno.clase)
        self.assertEqual(respuesta.context['ejercicios_asignados'][0],self.clase.ejercicios.all()[0])
        self.assertEqual(len(respuesta.context['ejercicios_asignados']),len(self.clase.ejercicios.all()))
        self.assertEqual(len(respuesta.context['ejercicios_realizados']),1)
        self.assertEqual(respuesta.context['ejercicios_realizados'][0],self.ejercicio)

        self.client.logout()

    def test_EjerciciosAsignados_context_is_correct_Profesor(self):
        """Probamos el contenido enviado a Ejercicios Asignados por un profesor"""
        login = self.client.force_login(user=self.profesor)
        ejercicio_asignado = Ejercicio.objects.create(curso=self.curso,tema=self.tema,titulo="Resta de números enteros",tipo=1,enunciado="¿Cuánto es 2-2?",soluciones="0;4;-4;-2",nsoluciones=1,solucion_correcta=0)
        self.clase.ejercicios.add(ejercicio_asignado)
        self.clase.ejercicios.add(self.ejercicio)
        self.clase.save()
        EJERCICIO_ASIGNADO_DIC={'ejercicio': ejercicio_asignado, 'alumnos': [], 'n_alumnos': 0}
        EJERCICIO_ASIGNADO_DIC2={'ejercicio': self.ejercicio, 'alumnos': [self.alumno], 'n_alumnos': 1}
        respuesta = self.client.get(reverse('ejerciciosAsignados',kwargs={'claseid':1}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['clase'],self.alumno.clase)
        self.assertEqual(respuesta.context['ejercicios_asignados'][0],EJERCICIO_ASIGNADO_DIC)
        self.assertEqual(respuesta.context['ejercicios_asignados'][1],EJERCICIO_ASIGNADO_DIC2)
        self.assertEqual(len(respuesta.context['ejercicios_asignados']),len(self.clase.ejercicios.all()))
        """Probamos cuando el get tiene un segundo parámetro con el id del ejercicio"""
        respuesta = self.client.get(reverse('ejerciciosAsignados',kwargs={'claseid':1,'ejercicioid':self.ejercicio.id}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['clase'],self.alumno.clase)
        self.assertEqual(respuesta.context['ejercicios_asignados'][0],EJERCICIO_ASIGNADO_DIC)
        self.assertEqual(respuesta.context['ejercicios_asignados'][1],EJERCICIO_ASIGNADO_DIC2)
        self.assertEqual(len(respuesta.context['ejercicios_asignados']),len(self.clase.ejercicios.all()))
        self.assertEqual(respuesta.context['alumnos'],[self.alumno])
        self.assertEqual(respuesta.context['ejercicio_seleccionado'],self.ejercicio)

        respuesta = self.client.get(reverse('ejerciciosAsignados',kwargs={'claseid':1,'ejercicioid':ejercicio_asignado.id}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['clase'],self.alumno.clase)
        self.assertEqual(respuesta.context['ejercicios_asignados'][0],EJERCICIO_ASIGNADO_DIC)
        self.assertEqual(respuesta.context['ejercicios_asignados'][1],EJERCICIO_ASIGNADO_DIC2)
        self.assertEqual(len(respuesta.context['ejercicios_asignados']),len(self.clase.ejercicios.all()))
        self.assertEqual(respuesta.context['alumnos'],[])
        self.assertEqual(respuesta.context['ejercicio_seleccionado'],ejercicio_asignado)
        """Probamos con un id de un ejercicio que no existe"""
        respuesta = self.client.get(reverse('ejerciciosAsignados',kwargs={'claseid':1,'ejercicioid':11}))
        self.assertFalse(respuesta.context['registro'])
        self.assertFalse(respuesta.context['alumno'])
        self.assertTrue(respuesta.context['profesor'])
        self.assertEqual(respuesta.context['clase'],self.alumno.clase)
        self.assertEqual(respuesta.context['ejercicios_asignados'][0],EJERCICIO_ASIGNADO_DIC)
        self.assertEqual(respuesta.context['ejercicios_asignados'][1],EJERCICIO_ASIGNADO_DIC2)
        self.assertEqual(len(respuesta.context['ejercicios_asignados']),len(self.clase.ejercicios.all()))
        
        self.client.logout()
    

