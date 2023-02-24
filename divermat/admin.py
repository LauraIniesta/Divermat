from django.contrib import admin
from divermat.models import (Profesor, Alumno, User, 
                    Clase, Curso, Ejercicio,
                    Examen, Video, Resumen,Tema, Usuario, Foto)

# Register your models here.
admin.site.register(Profesor)
admin.site.register(Alumno)
admin.site.register(Clase)
admin.site.register(Curso)
admin.site.register(Ejercicio)
admin.site.register(Video)
admin.site.register(Resumen)
admin.site.register(Tema)
admin.site.register(Examen)
admin.site.register(Foto)
