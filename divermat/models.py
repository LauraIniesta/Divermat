from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Usuario(User):
    tipo = models.BooleanField(default=1, choices=[(0,'Profesor'),(1,'Alumno')], null=True)
    centro = models.CharField(max_length=150, default=None, null=True)

    #Una lista con sus clases ¿?.
    class Meta:
        """ordering = ('first_name', 'last_name', )"""
        abstract = True
        #  imprimir en orden de last_name,first_name

    def __str__(self):
        return self.first_name + " " + self.last_name


class Curso(models.Model):
    curso = models.CharField(max_length=1, default=None)

    class Meta:
        ordering = ('curso', )

    def __str__(self):
        return self.curso


class Tema(models.Model):
    tema = models.IntegerField(default=None, null=True) 
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE,
                              default=None, null= True)
    titulo = models.CharField(default=None, max_length=150)
    
    class Meta:
        ordering = ('tema', 'curso', )

    def __str__(self):
        return  str(self.curso) + "ESO Tema:" + str(self.tema) + ". " + self.titulo


class Profesor(Usuario):

    #Una lista con sus clases ¿?.
    class Meta:
        ordering = ('first_name', 'last_name', )
        #  imprimir en orden de last_name,first_name

    def __str__(self):
        return self.first_name + " " + self.last_name

class Ejercicio(models.Model):
    curso = models.ForeignKey(Curso,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    tema = models.ForeignKey(Tema,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    titulo = models.CharField(max_length=50, default=None)
    tipo = models.IntegerField(default=None,null=True) # Tipo 1 es test, tipo 2 respuesta corta, tipo 3 problemas pero ese todavía no lo implemento
    enunciado = models.CharField(max_length=1000, default = None)
    nsoluciones = models.IntegerField(default=None,null=True)
    soluciones = models.CharField(max_length=1000, default = None) #Cada solucion divididad por ; o algo así tupla que ponga valor y si es o no correta
    #Primero tipo test y respuesta con hueco problemas más adelante un ej tipo por curso y temática

    class Meta:
        ordering = ('curso',  'titulo', )

    def __str__(self):
        return str(self.curso) +  " " + self.titulo


class Clase(models.Model):
    #Se crean clases con los mismos datos corregirlo algo con primary key
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE,
                              default=None, null=True) #Hacerlo con choices valores 1 2 3 y 4 e internamente hacer la referencia
    nombre = models.CharField(max_length=15, default=None)
    centro = models.CharField(max_length=150, default=None)
    ano_academico = models.DateField()
    n_alumnos = models.IntegerField(default=None,null=True)
    profesor = models.ForeignKey(Profesor,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    ejercicios = models.ManyToManyField(Ejercicio,
                                 default=None)#Lista con un dic que tenga los ids de los ejercicios asignados y lista alum hecho
    
    class Meta:
        ordering = ('ano_academico','curso', 'nombre', 'centro', )
        #  imprimir en orden de last_name,first_name

    def __str__(self):
        return str(self.curso) + "º ESO " + self.nombre + " " + str(self.ano_academico) + " " + self.centro

class Alumno(Usuario):
    #User ya tiene name username y last name
    password_temporal = models.CharField(max_length=15,default=None,null=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE,
                              default=0, null=True)

    clase = models.ForeignKey(Clase, on_delete=models.CASCADE, default=None, null=True)
    numexamen = models.IntegerField(default=0,null=True)
    #Una lista con sus clases ¿?.
    class Meta:
        ordering = ('first_name', 'last_name', )
        #  imprimir en orden de last_name,first_name

    def __str__(self):
        return self.first_name + " " + self.last_name + "-" + self.username


class Video(models.Model):
    curso = models.ForeignKey(Curso,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    tema = models.ForeignKey(Tema,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    titulo = models.CharField(max_length=50, default=None)
    #Link o video ver como se cargan

    class Meta:
        ordering = ('curso', 'tema', 'titulo', )

    def __str__(self):
        return str(self.curso) + " " + str(self.tema) + " " + self.titulo


class Resumen(models.Model):

    curso = models.ForeignKey(Curso,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    tema = models.ForeignKey(Tema,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    titulo = models.CharField(max_length=50, default=None) 
    texto =  models.CharField(max_length=10000, default=None)

    class Meta:
        ordering = ('curso', 'tema', 'titulo', )

    def __str__(self):
        return str(self.curso) + " " + str(self.tema) + " " + self.titulo


class Examen(models.Model):
    titulo = models.CharField(max_length=200, default=None) #COmbinará el usuario con el curso y tema
    alumno = models.ForeignKey(Alumno, 
                                on_delete=models.CASCADE,
                                default=None, null=True)
    curso = models.ForeignKey(Curso,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    temas = models.ManyToManyField(Tema,
                                 default=None) #el usuario seleccionará varios temas
    ejercicios = models.ManyToManyField(Ejercicio,
                                 default=None) #Ids de los ejercicios del examen
    cronometrado = models.CheckConstraint(name="Cronometrado", check=['Si', 'No'])
    tiempo = models.FloatField(default=None,null=True) # Tengo que decidir tipos de ejs y ponerlos con numeracion
    
    class Meta:
        ordering = ('curso', 'titulo', )

    def __str__(self):
        return str(self.curso) + " " + self.titulo + " "

class Seguimiento(models.Model):
    alumno = models.ForeignKey(Alumno, 
                                on_delete=models.CASCADE,
                                default=None, null=True)
    tema = models.ForeignKey(Tema,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    ejercicios = models.ManyToManyField(Ejercicio,
                                default=None) #Ids de los ejercicios que ha realizado
    n_ejercicios = models.IntegerField(default=0,null=True)
    acierto = models.FloatField(default=0.0, null=True)
    
    class Meta:
        ordering = ('tema',  )

    def __str__(self):
        return self.alumno + " " + self.tema + " "
