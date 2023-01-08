from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'index', views.index, name='index'),
    url(r'perfil', views.perfil, name='perfil'),
    url(r'cerrar_sesion', views.cerrar_sesion.as_view(), name='cerrar_sesion'),
    url(r'iniciar_sesion', views.iniciar_sesion, name='iniciar_sesion'),
    # url(r'iniciar_sesion_alumno_profesor',views.iniciar_sesion_alumno_profesor,name='iniciar_sesion_alumno_profesor'),
    url(r'registro', views.registro.as_view(), name='registro'),
    url(r'videos', views.videos, name='videos'),
    url(r'resumenes', views.resumenes, name='resumenes'),
    url(r'examenes', views.examenes, name='examenes'),
    url(r'ejercicio', views.ejercicio, name='ejercicio'),
    url(r'video', views.video, name='video'),
    url(r'resumen', views.resumen, name='resumen'),
    url(r'clases', views.clases, name='clases'),
    url(r'^clase/(?P<clase>[\w]+)/$', views.clase, name='clase'),
    url(r'^clase', views.clase, name='clase'),
    url(r'infoclase/(?P<claseid>[\w]+)/$', views.infoclase, name='infoclase'),
    url(r'alumnosclase/(?P<claseid>[\w]+)/$', views.alumnosclase, name='alumnosclase'),
    url(r'seguimientoclase/(?P<claseid>[\w]+)/$', views.seguimientoclase, name='seguimientoclase'),
    url(r'^alumnos/(?P<alumno>[\w]+)/$', views.alumnos, name='alumnos'),
    url(r'^alumnos', views.alumnos, name='alumnos'),
    url(r'contenido', views.contenido, name='contenido'),
    url(r'^cambiar_contrasenia', views.PasswordChangeView.as_view(), name='cambiar_contrasenia'),
    url(r'^cambiarInformacionAlumno',views.cambiarInformacionAlumno,name='cambiarInformacionAlumno'),
]