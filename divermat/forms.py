
from sqlite3 import Date
from tkinter.tix import Select
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime
from divermat.models import Curso, Tema, Examen, Profesor, Alumno, Clase


class NuevoExamen(forms.Form):
    
    crono = forms.ChoiceField(label="¿Quieres que el examen sea cronometrado?",choices=[(True,'Si'), (False,'No')],required=True, initial='Si')
    temas = forms.ModelMultipleChoiceField(label="Selecciona el Temario del examen",queryset=Tema.objects,widget=forms.widgets.CheckboxSelectMultiple,required=True)

    def __init__(self, *args, **kwargs):
        c = kwargs.pop('curso', None)
        super(NuevoExamen,self).__init__(*args, **kwargs)
        if c:
            self.fields['temas'].queryset = Tema.objects.filter(curso=c)

    def clean_input(self):
        data = self.cleaned_data
        return data


class NuevoSetEjercicios(forms.Form):

    tema = forms.ModelChoiceField(label="",queryset=Tema.objects,widget=forms.widgets.Select(),required=True, initial="Tema")

    def __init__(self, *args, **kwargs):
        c = kwargs.pop('curso', None)
        super(NuevoSetEjercicios,self).__init__(*args, **kwargs)
        if c:
            self.fields['tema'].queryset = Tema.objects.filter(curso=c)

    def clean_input(self):
        data = self.cleaned_data
        return data


class Registro(UserCreationForm):

    class Meta:
        model = Profesor
        fields = (
            'first_name',
            'last_name',
            'centro',
            'username',
            'email',
            'password1',
            'password2',
            
        )


class NuevaClase(forms.ModelForm):

    class Meta:
        model = Clase
        fields = (
            'curso',
            'nombre',
            'ano_academico',
            'n_alumnos',
        )

        labels = {
            'nombre': ('Nombre'),
            'curso': ('Curso'),
            'ano_academico':('Fecha de Inicio'),
            'n_alumnos':('Número de alumnos'),
        }


class NuevaInfoProfesor(forms.ModelForm):

    username = forms.CharField(label="Nombre de usuario:",max_length=150,required=False)
    centro = forms.CharField(label="Centro educativo:",max_length=150,required=False)

    class Meta:
        model = Profesor
        fields = (
            'username',
            'centro',
        )


class NuevaInfoAlumno(forms.ModelForm):
    first_name = forms.CharField(label="Nombre:",max_length=150,required=False)
    last_name = forms.CharField(label="Apellidos:",max_length=150,required=False)
    
    class Meta:
        model = Alumno
        fields = (
            'first_name',
            'last_name',
        )


class NuevaInfoClase(forms.ModelForm):
    nombre = forms.CharField(max_length=15,required=False)
    curso = forms.ModelChoiceField(queryset=Curso.objects,required=False, widget=forms.widgets.Select(),initial='Curso')
    centro = forms.CharField(max_length=150, required=False)
    ano_academico = forms.DateField(label="Fecha de Inicio:",required=False)
    class Meta:
        model = Clase
        fields = [
            'nombre',
            'curso',
            'ano_academico',
            'centro',
            ]


class NuevoAlumno(forms.Form):
    
    n_alumnos = forms.IntegerField(label="Indica el nº de alumnos")
    
    def clean_input(self):
        data = self.cleaned_data
        return data


class InicioSesion(forms.Form):
    username=forms.CharField(max_length=255,label="Introduce tu nombre de usuario:")
    password=forms.CharField(max_length=255,widget=forms.PasswordInput)

    def clean_input(self):
        data = self.cleaned_data
        return data

       


