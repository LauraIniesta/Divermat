from datetime import datetime
import pickle

from django.test import TestCase
from os.path import join

from divermat.forms import (NuevoExamen,NuevoSetEjercicios, 
                            NuevaClase,NuevaInfoProfesor, NuevaInfoAlumno,
                            NuevaInfoClase,NuevoAlumno,InicioSesion)

from divermat.models import *

class FormsTests(TestCase):
    """En esta clase vamos a probar el correcto funcionamiento de los formularios"""
    @classmethod
    def setUpTestData(self):
        self.curso = Curso.objects.create(curso=1)
        self.curso2 = Curso.objects.create(curso=2)
        self.tema = Tema.objects.create(tema=1, curso=self.curso, titulo="Números Naturales")
        self.tema2 = Tema.objects.create(tema=3, curso=self.curso2, titulo="Ecuaciones")
        self.profesor = Profesor.objects.create(username="profe",first_name="Profesor", last_name="Prueba", tipo=0)
        self.ejercicio = Ejercicio.objects.create(curso=self.curso,tema=self.tema,titulo="Suma de números enteros",tipo=2,enunciado="¿Cuánto es 2+2?",soluciones="2;4;3;5",nsoluciones=1,solucion_correcta=4)
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

    def test_nuevo_examen_form(self):
        """Comprobamos que el formulario nuevo examen contiene los datos, label etc a mostrar correctos"""
        form = NuevoExamen()
        self.assertEqual(form.fields['crono'].label , '¿Quieres que el examen sea cronometrado?')
        self.assertEqual(form.fields['temas'].label , 'Selecciona el Temario del examen')
        self.assertEqual(form.fields['temas'].queryset[0],Tema.objects.all()[0])
        self.assertEqual(form.fields['temas'].queryset[1],Tema.objects.all()[1])
        self.assertEqual(len(form.fields['temas'].queryset),len(Tema.objects.all()))
        form2 = NuevoExamen(curso=1)
        self.assertEqual(form2.fields['crono'].label , '¿Quieres que el examen sea cronometrado?')
        self.assertEqual(form2.fields['temas'].label , 'Selecciona el Temario del examen')
        self.assertEqual(form2.fields['temas'].queryset[0],self.tema)
        self.assertEqual(len(form2.fields['temas'].queryset),1)
    
    def test_required_attributes_nuevo_examen_form(self):
        """Comprobamos que para el formulario Nuevo Examen
        el método is valid con los campos required devuelve false si falta alguno"""
        temas = []
        temas.append(self.tema.id)

        data = {'crono': True,'temas':temas}
        form = NuevoExamen(data)
        self.assertTrue(form.is_valid())

        data = {'crono':True}
        form = NuevoExamen(data)
        self.assertFalse(form.is_valid())

        data = {'temas':temas}
        form = NuevoExamen(data)
        self.assertFalse(form.is_valid())

        data = {}
        form = NuevoExamen(data)
        self.assertFalse(form.is_valid())


    def test_nuevo_set_ejercicios(self):
        """Comprobamos que el formulario set de ejercicios contiene los datos, label etc a mostrar correctos"""
        form = NuevoSetEjercicios()
        self.assertTrue(form.fields['tema'].label == '')
        self.assertEqual(form.fields['tema'].queryset[0],Tema.objects.all()[0])
        self.assertEqual(form.fields['tema'].queryset[1],Tema.objects.all()[1])
        self.assertEqual(len(form.fields['tema'].queryset),len(Tema.objects.all()))
        form2 = NuevoSetEjercicios(curso=1)
        self.assertEqual(form2.fields['tema'].queryset[0],self.tema)
        self.assertEqual(len(form2.fields['tema'].queryset),1)
    
    def test_required_attributes_nuevo_set_ejercicios_form(self):
        """Comprobamos que para el formulario Set de Ejericios el método is valid
        con los campos required devuelve false si falta alguno"""
        data = {'tema':self.tema}
        form = NuevoSetEjercicios(data)
        self.assertTrue(form.is_valid())

        data = {}
        form = NuevoSetEjercicios(data)
        self.assertFalse(form.is_valid())

    def test_nueva_clase(self):
        """Comprobamos que el formulario nueva clase contiene los datos, label etc a mostrar correctos"""
        form = NuevaClase()
        self.assertEqual(form.fields['curso'].label , 'Curso')
        self.assertEqual(form.fields['nombre'].label , 'Nombre')
        self.assertEqual(form.fields['ano_academico'].label , 'Fecha de Inicio')
        self.assertEqual(form.fields['n_alumnos'].label , 'Número de alumnos')

    def test_content_nueva_clase_form(self):
        """Comprobamos que para el formulario nueva clase, el método is valid 
        devuelve false si el contenido de los atributos no es correcto"""
        data = {'curso': self.curso,'nombre':'A', 'ano_academico':datetime.now(),'n_alumnos':'10'}
        form = NuevaClase(data)
        self.assertTrue(form.is_valid())

        data = {'curso': self.curso,'nombre':'A', 'ano_academico':'str','n_alumnos':'10'}
        form = NuevaClase(data)
        self.assertFalse(form.is_valid())

        data = {'curso': self.curso,'nombre':'A', 'ano_academico':'10','n_alumnos':'10'}
        form = NuevaClase(data)
        self.assertFalse(form.is_valid())

        data = {'curso': self.curso,'nombre':'A', 'ano_academico':datetime.now(),'n_alumnos':'str'}
        form = NuevaClase(data)
        self.assertFalse(form.is_valid())

    def test_required_attributes_nueva_clase_form(self):
        """Comprobamos que para el formulario Nueva Clase el método is valid 
        con los campos required devuelve false si falta alguno"""
        data = {'curso': self.curso,'nombre':'A', 'ano_academico':datetime.now(),'n_alumnos':'10'}
        form = NuevaClase(data)
        self.assertTrue(form.is_valid())

        data = {'nombre':'A', 'ano_academico':datetime.now(),'n_alumnos':'10'}
        form = NuevaClase(data)
        self.assertFalse(form.is_valid())
        
        data = {'curso': self.curso,'ano_academico':datetime.now(),'n_alumnos':'10'}
        form = NuevaClase(data)
        self.assertFalse(form.is_valid())

        data = {'curso': self.curso,'nombre':'A', 'n_alumnos':'10'}
        form = NuevaClase(data)
        self.assertFalse(form.is_valid())

        data = {'curso': self.curso,'nombre':'A', 'ano_academico':datetime.now()}
        form = NuevaClase(data)
        self.assertFalse(form.is_valid())

        data = {}
        form = NuevaClase(data)
        self.assertFalse(form.is_valid())


    def test_nueva_info_profesor(self):
        """Comprobamos que el formulario Nueva Info Profesor contienen los datos, label etc a mostrar correctos"""
        form = NuevaInfoProfesor()
        self.assertEqual(form.fields['username'].label , 'Nombre de usuario:')
        self.assertEqual(form.fields['centro'].label , 'Centro educativo:')
        self.assertEqual(form.fields['username'].max_length , 150)
        self.assertEqual(form.fields['centro'].max_length , 150)


    def test_required_attributes_nueva_info_profesor_form(self):
        """Comprobamos que para el formulario Nueva Info Profesor el método is valid 
        devuelve true siempre ya que ninguno de sus campos es required"""
        data = {'username': 'profeusername','centro':'centro'}
        form = NuevaInfoProfesor(data)
        self.assertTrue(form.is_valid())

        data = {'username': 'profeusername'}
        form = NuevaInfoProfesor(data)
        self.assertTrue(form.is_valid())

        data = {'centro':'centro'}
        form = NuevaInfoProfesor(data)
        self.assertTrue(form.is_valid())

        data = {}
        form = NuevaInfoProfesor(data)
        self.assertTrue(form.is_valid())

    
    def test_nueva_info_alumno(self):
        """Comprobamos que los formularios contienen los datos, label etc a mostrar correctos"""
        form = NuevaInfoAlumno()
        self.assertEqual(form.fields['first_name'].label , 'Nombre:')
        self.assertEqual(form.fields['last_name'].label , 'Apellidos:')
        self.assertEqual(form.fields['first_name'].max_length , 150)
        self.assertEqual(form.fields['last_name'].max_length , 150)


    def test_required_attributes_nueva_info_alumno_form(self):
        """Comprobamos que para el formulario Nueva Info Alumno el método is valid 
        devuelve true siempre ya que ninguno de sus campos es required"""
        data = {'first_name': 'alumnoname','last_name':'alumnosurname'}
        form = NuevaInfoAlumno(data)
        self.assertTrue(form.is_valid())

        data = {'first_name': 'alumnoname'}
        form = NuevaInfoAlumno(data)
        self.assertTrue(form.is_valid())

        data = {'last_name':'alumnosurname'}
        form = NuevaInfoAlumno(data)
        self.assertTrue(form.is_valid())

        data = {}
        form = NuevaInfoAlumno(data)
        self.assertTrue(form.is_valid())


    def test_nueva_info_clase(self):
        """Comprobamos que el formulario Nueva Info Clase contiene los datos, label etc a mostrar correctos"""
        form = NuevaInfoClase()
        self.assertEqual(form.fields['nombre'].label , None)
        self.assertEqual(form.fields['curso'].label , None)
        self.assertEqual(form.fields['centro'].label , None)
        self.assertEqual(form.fields['ano_academico'].label , 'Fecha de Inicio:')
        self.assertEqual(form.fields['nombre'].max_length , 15)
        self.assertEqual(form.fields['centro'].max_length , 150)
        self.assertEqual(form.fields['curso'].queryset[0] ,Curso.objects.all()[0])
        self.assertEqual(len(form.fields['curso'].queryset) ,len(Curso.objects.all()))


    def test_required_attributes_nueva_info_clase_form(self):
        """Comprobamos que para el formulario Nueva Info Clase el método is valid 
        devuelve true siempre ya que ninguno de sus campos es required"""
        data = {'curso': self.curso,'nombre':'A', 'ano_academico':datetime.now(),'n_alumnos':'10'}
        form = NuevaInfoClase(data)
        self.assertTrue(form.is_valid())

        data = {'nombre':'A', 'ano_academico':datetime.now(),'n_alumnos':'10'}
        form = NuevaInfoClase(data)
        self.assertTrue(form.is_valid())
        
        data = {'curso': self.curso,'ano_academico':datetime.now(),'n_alumnos':'10'}
        form = NuevaInfoClase(data)
        self.assertTrue(form.is_valid())

        data = {'curso': self.curso,'nombre':'A', 'n_alumnos':'10'}
        form = NuevaInfoClase(data)
        self.assertTrue(form.is_valid())

        data = {'curso': self.curso,'nombre':'A', 'ano_academico':datetime.now()}
        form = NuevaInfoClase(data)
        self.assertTrue(form.is_valid())

        data = {}
        form = NuevaInfoClase(data)
        self.assertTrue(form.is_valid())

    def test_content_nueva_info_clase_form(self):
        """Comprobamos que Nueva Info Clase el método is valid devuelve false si el contenido de los atributos no es correcto"""
        data = {'curso': self.curso,'nombre':'A', 'ano_academico':datetime.now(),'n_alumnos':'10'}
        form = NuevaInfoClase(data)
        self.assertTrue(form.is_valid())

        data = {'curso': self.curso,'nombre':'A', 'ano_academico':'str','n_alumnos':'10'}
        form = NuevaInfoClase(data)
        self.assertFalse(form.is_valid())

        data = {'curso': self.curso,'nombre':'A', 'ano_academico':'10','n_alumnos':'10'}
        form = NuevaInfoClase(data)
        self.assertFalse(form.is_valid())


    def test_nuevo_alumno(self):
        """Comprobamos que el formulario Nuevo Alumno contiene los datos, label etc a mostrar correctos"""
        form = NuevoAlumno()
        self.assertEqual(form.fields['n_alumnos'].label , 'Indica el nº de alumnos')


    def test_required_attributes_nuevo_alumno_form(self):
        """Comprobamos que para el formulario Nuevo Alumno el método is valid 
        devuelve true siempre ya que ninguno de sus campos es required"""
        data = {'n_alumnos': 2}
        form = NuevoAlumno(data)
        self.assertTrue(form.is_valid())

        data = {}
        form = NuevoAlumno(data)
        self.assertFalse(form.is_valid())

    def test_content_nuevo_alumno_form(self):
        """Comprobamos que para el formulario Nuevo Alumno el método is valid 
        devuelve true siempre ya que ninguno de sus campos es required"""
        data = {'n_alumnos': 2}
        form = NuevoAlumno(data)
        self.assertTrue(form.is_valid())

        data = {'n_alumnos': 'str'}
        form = NuevoAlumno(data)
        self.assertFalse(form.is_valid())


    def test_inicio_sesion(self):
        """Comprobamos que el formulario Inicio Sesion contienen los datos, label etc a mostrar correctos"""
        form = InicioSesion()
        self.assertEqual(form.fields['username'].label,'Introduce tu nombre de usuario:')
        self.assertEqual(form.fields['username'].max_length,255)
        self.assertEqual(form.fields['password'].max_length,255)


    def test_required_attributes_inicio_sesion_form(self):
        """Comprobamos que para el formulario Inicio de Sesion el método is valid devuelve true siempre ya que ninguno de sus campos es required"""
        data = {'username': 'alumnousername','password':'password'}
        form = InicioSesion(data)
        self.assertTrue(form.is_valid())

        data = {'username': 'alumnousername'}
        form = InicioSesion(data)
        self.assertFalse(form.is_valid())

        data = {'password':'password'}
        form = InicioSesion(data)
        self.assertFalse(form.is_valid())

        data = {}
        form = InicioSesion(data)
        self.assertFalse(form.is_valid())
