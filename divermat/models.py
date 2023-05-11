from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Usuario(User):
    #0 se corresponde con False (Profesor) y 1 con True (Alumno)
    tipo = models.BooleanField(default=1, choices=[(0,'Profesor'),(1,'Alumno')], null=True)
    centro = models.CharField(max_length=150, default=None, null=True)

    #Una lista con sus clases ¿?.
    class Meta:
        """ordering = ('first_name', 'last_name', )"""
        abstract = True
        #  imprimir en orden de last_name,first_name

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)


class Curso(models.Model):
    curso = models.CharField(max_length=1, default=None)

    class Meta:
        ordering = ('curso', )

    def __str__(self):
        return str(self.curso)


class Tema(models.Model):
    tema = models.IntegerField(default=None, null=True) 
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE,
                              default=None, null= True)
    titulo = models.CharField(default=None, max_length=150)
    
    class Meta:
        ordering = ('curso', 'tema', )

    def __str__(self):
        return  str(self.curso) + "º ESO Tema:" + str(self.tema) + ". " + self.titulo


class Profesor(Usuario):

    #Una lista con sus clases ¿?.
    class Meta:
        ordering = ('first_name', 'last_name', )
        #  imprimir en orden de last_name,first_name

    def __str__(self):
        return str(self.first_name) + " " + str(self.last_name)

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
    nsoluciones = models.IntegerField(default=None,null=True) #Numero de soluciones correctas
    soluciones = models.CharField(max_length=1000, default = None) #Cada solucion divididad por ; incluye la solucion correcta y las erroneas en caso de Test
    solucion_correcta = models.CharField(max_length=1024, default = None)
    foto = models.FileField(upload_to='media/fotos/%y',blank=True,null=False)
    
    
    #Primero tipo test y respuesta con hueco problemas más adelante un ej tipo por curso y temática

    class Meta:
        ordering = ('curso',  'titulo', )

    def __str__(self):
        return str(self.curso) +  "ºESO " + self.titulo


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
        return str(self.curso) + "º ESO " + str(self.nombre) + " " + str(self.ano_academico) + " " + str(self.centro)

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
        return str(self.first_name) + " " + str(self.last_name) + "-" + str(self.username)

class VideoFile(models.Model):
    
    tituloFile = models.CharField(max_length=50, default=None)
    videoFile = models.FileField(upload_to='media/videos/%y',blank=True,null=False)
    
    def __str__(self):
        return str(self.tituloFile)
    
class Video(models.Model):
    curso = models.ForeignKey(Curso,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    tema = models.ForeignKey(Tema,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    titulo = models.CharField(max_length=50, default=None)
    
    video = models.ForeignKey(VideoFile,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)

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
    resumen = models.FileField(upload_to='media/resumenes',blank=True,null=True)

    class Meta:
        ordering = ('curso', 'tema', 'titulo', )

    def __str__(self):
        return str(self.curso) + " " + str(self.tema) + " " + self.titulo


class EjercicioUsuario(models.Model):
    ejercicio = models.ForeignKey(Ejercicio,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    alumno = models.ForeignKey(Alumno,
                                on_delete=models.CASCADE,
                                default=None, null=True)
    soluciones_seleccionadas = models.CharField(max_length=1000, default = None) #Cada solucion divididad por ; incluye las seleccionadas por el usuario

    resultado = models.CharField(max_length=1000, default = None, null=True)

    def __str__(self):
        return str(self.ejercicio) + " " + str(self.alumno) + " " + str(self.resultado)


class Examen(models.Model):
    titulo = models.CharField(max_length=200, default=None) #COmbinará el usuario con el curso y tema
    alumno = models.ForeignKey(Alumno, 
                                on_delete=models.CASCADE,
                                default=None, null=True)
    curso = models.ForeignKey(Curso,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    temas = models.ManyToManyField(Tema) #el usuario seleccionará varios temas
    ejercicios = models.ManyToManyField(EjercicioUsuario,
                                 default=None)#Lista con un dic que tenga los ids de los ejercicios asignados y lista alum hecho
    cronometrado = models.BooleanField(default=1, choices=[(0,'Si'),(1,'No')], null=True)
    inicio = models.DateTimeField(default=None,null=False)
    fin=models.DateTimeField(default=None,null=True)
    nota = models.FloatField(default=0,null=True)
    
    class Meta:
        ordering = ('curso', 'titulo', )

    def __str__(self):
        return str(self.curso) + " " + str(self.titulo)

class Seguimiento(models.Model):
    alumno = models.ForeignKey(Alumno, 
                                on_delete=models.CASCADE,
                                default=None, null=True)
    tema = models.ForeignKey(Tema,
                                 on_delete=models.CASCADE,
                                 default=None, null=True)
    ejercicios = models.ManyToManyField(Ejercicio,
                                default=None)
    n_ejercicios = models.IntegerField(default=0,null=True)
    acierto = models.FloatField(default=0.0, null=True)
    
    class Meta:
        ordering = ('tema',  )

    def __str__(self):
        return str(self.alumno) + " " + str(self.tema)