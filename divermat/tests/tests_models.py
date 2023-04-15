from datetime import datetime
import pickle

from django.test import TestCase
from os.path import join

from divermat.models import *

class ModelTests(TestCase):
    """En esta clase sa va a probar el funcionamiento de los Modelos"""
    @classmethod
    def setUpTestData(self):
        self.curso = Curso.objects.create(curso=1)
        self.tema = Tema.objects.create(tema=1, curso=self.curso, titulo="Números Naturales")
        self.profesor = Profesor.objects.create(username="profe",first_name="Profesor", last_name="Prueba", tipo=0)
        self.ejercicio = Ejercicio.objects.create(curso=self.curso,tema=self.tema,titulo="Suma de números enteros",tipo=2,enunciado="¿Cuánto es 2+2?",soluciones="2;4;3;5",nsoluciones=1,solucion_correcta=4)
        self.clase = Clase.objects.create(curso=self.curso,nombre="A",centro="IES Prueba",ano_academico=datetime.now(timezone.utc), n_alumnos=1,profesor=self.profesor)
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
        self.resumen = Resumen.objects.create(texto="........",curso=self.curso,tema=self.tema,titulo="Resolución de sumas de Números naturales")


    def test_str_functions_of_all_models(self):
        """Probamos que el método str de todos los Modelos devuelte la string esperada"""
        #Probamos el método str del modelo curso
        curso_str = "1"
        self.assertEqual(curso_str,str(self.curso))
        #Probamos el método str del modelo Tema
        tema_str = "1º ESO Tema:1. Números Naturales"
        self.assertEqual(tema_str,str(self.tema))
        #Probamos el método str del modelo Profesor
        profesor_str = "Profesor Prueba"
        self.assertEqual(profesor_str,str(self.profesor))
        #Probamos el método str del modelo Ejercicio
        ejercicio_str = "1ºESO Suma de números enteros"
        self.assertEqual(ejercicio_str,str(self.ejercicio))
        #Probamos el método str del modelo Clase
        clase_str = "1º ESO A "+str(self.clase.ano_academico)+" IES Prueba"
        self.assertEqual(clase_str,str(self.clase))
        #Probamos el método str del modelo Alumno
        alumno_str = "Alumno Prueba-alumno"
        self.assertEqual(alumno_str,str(self.alumno))
        #Probamos el método str del modelo Examen
        examen_str = "1 Examen tema 1"
        self.assertEqual(examen_str,str(self.examen))
        #Probamos el método str del modelo Seguimiento
        seguimiento_str = "Alumno Prueba-alumno 1º ESO Tema:1. Números Naturales"
        self.assertEqual(seguimiento_str,str(self.seguimiento))
        #Probamos el método str del modelo EjercicioUsuario
        ejusuario_str = "1ºESO Suma de números enteros Alumno Prueba-alumno ¡Respuesta Correcta!"
        self.assertEqual(ejusuario_str,str(self.ejercicioUsuario))
        #Pronamos el método str del modelo Resumen
        resumen_str="1 1º ESO Tema:1. Números Naturales Resolución de sumas de Números naturales"
        self.assertEqual(resumen_str,str(self.resumen))


    def test_length_of_attributes_from_Tema(self):
        """Probamos que la longitud máxima de los atributos del Modelo Tema es correcta"""
        tema=Tema.objects.get(id=1)
        max_length = tema._meta.get_field('titulo').max_length
        self.assertEqual(max_length,150)


    def test_length_of_attributes_from_ejercicio(self):
        """Probamos que la longitud máxima de los atributos del Modelo Ejercicio es correcta"""
        ejercicio=Ejercicio.objects.get(id=1)
        max_length = ejercicio._meta.get_field('titulo').max_length
        self.assertEqual(max_length,50)

        max_length = ejercicio._meta.get_field('enunciado').max_length
        self.assertEqual(max_length,1000)

        max_length = ejercicio._meta.get_field('soluciones').max_length
        self.assertEqual(max_length,1000)

        max_length = ejercicio._meta.get_field('solucion_correcta').max_length
        self.assertEqual(max_length,1024)


    def test_length_of_attributes_from_clase(self):
        """Probamos que la longitud máxima de los atributos del Modelo Clase es correcta"""
        clase=Clase.objects.get(id=1)
        max_length = clase._meta.get_field('nombre').max_length
        self.assertEqual(max_length,15)

        max_length = clase._meta.get_field('centro').max_length
        self.assertEqual(max_length,150)


    def test_length_of_attributes_from_profesor(self):
        """Probamos que la longitud máxima de los atributos del Modelo Profesor es correcta"""
        profesor=Profesor.objects.get(id=1)
        max_length = profesor._meta.get_field('centro').max_length
        self.assertEqual(max_length,150)


    def test_length_of_attributes_from_alumno(self):
        """Probamos que la longitud máxima de los atributos del Modelo Alumno es correcta"""
        alumno=Alumno.objects.get(id=2)
        max_length = alumno._meta.get_field('password_temporal').max_length
        self.assertEqual(max_length,15)

        max_length = alumno._meta.get_field('centro').max_length
        self.assertEqual(max_length,150)
    

    def test_length_of_attributes_from_ejercicioUsuario(self):
        """Probamos que la longitud máxima de los atributos del Modelo EjercicioUsuario es correcta"""

        ejercicioUsuario=EjercicioUsuario.objects.get(id=1)
        max_length = ejercicioUsuario._meta.get_field('soluciones_seleccionadas').max_length
        self.assertEqual(max_length,1000)

        max_length = ejercicioUsuario._meta.get_field('resultado').max_length
        self.assertEqual(max_length,1000)

    
    def test_length_of_attributes_from_examen(self):
        """Probamos que la longitud máxima de los atributos del Modelo Examen es correcta"""
        examen=Examen.objects.get(id=1)
        max_length = examen._meta.get_field('titulo').max_length
        self.assertEqual(max_length,200)

    def test_length_of_attributes_from_resumen(self):
        """Probamos que la longitud máxima de los atributos del Modelo Resumen es correcta"""
        resumen=Resumen.objects.get(id=1)
        max_length = resumen._meta.get_field('texto').max_length
        self.assertEqual(max_length,10000)
        max_length = resumen._meta.get_field('titulo').max_length
        self.assertEqual(max_length,50)