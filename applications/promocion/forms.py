import datetime

from django import forms

from .models import Desarrollo, Programa_Actualizaciones, Visita, Visita_Detalle, Evento
from applications.home.models import Codigos_Maestros

class VisitaForm(forms.ModelForm):

    rfc = forms.CharField(
        max_length=13,
        label='RFC:',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'

            }
        )
    )

    nombre = forms.CharField(
        max_length=200,
        label='Nombre:',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nombre Apellido Paterno Apellido Materno'
            }
        )
    )

    fecha = forms.DateField(
        label='Fecha:',
        required=True,
        initial=datetime.date.today,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'value': 'Select Date',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy',
                'style': 'display:none'
            }
        )
    )

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(VisitaForm, self).__init__(*args, **kwargs)

        self.fields['id_desarrollo'] = forms.ModelChoiceField(
            queryset=Desarrollo.objects.filter(pk=pk),
            required=True,
            initial=0,
            widget=forms.Select(
                attrs={
                    'class': 'form-control',
                    'style': 'display:none'
                }
            )
        )

    class Meta:
        model = Visita
        fields = ["id_desarrollo", "rfc", "nombre", "fecha"]




class ProgramaForm(forms.ModelForm):

    nombre = forms.CharField(
        max_length=200,
        label='Nombre:',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    descripcion = forms.CharField(
        max_length=600,
        label='Descripcion:',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '5'
            }
        )
    )

    objetivo = forms.CharField(
        max_length=600,
        label='Objetivo:',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '5'
            }
        )
    )

    estatus = forms.CharField(
        max_length=100,
        label='Estatus:',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'style': 'display:none'
            }
        )
    )

    class Meta:
        model = Programa_Actualizaciones
        fields = ["nombre", "descripcion", "objetivo", "estatus"]


class AprobarForm(forms.Form):

    comentarios = forms.CharField(
        max_length=600,
        label='Comentarios:',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '5'
            }
        )
    )

    estatus = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXPROGRAM_PROMOCION'),
       label = 'Estatus:', 
       initial = 0,
       widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

class DesarrolloForm(forms.ModelForm): 
    
    class Meta:
        model = Desarrollo
        fields = ["id_evento", "fecha_inicio", "fecha_fin","jefatura",
                  "fecha_inicio_campo", "fecha_fin_campo", "estatus","comentarios",
                  "fecha_inicio_calidad", "fecha_fin_calidad","responsables"]


class EventoForm(forms.ModelForm): 

    nombre = forms.CharField(
        max_length=200,
        label = 'Nombre:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    id_programa = forms.ModelChoiceField(
       queryset = Programa_Actualizaciones.objects.all(),
       label = 'Programa:',
       initial = 0,
       required=True,
       widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    direccion = forms.CharField(
        max_length=400,
        label = 'Direccion:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    ciudad = forms.CharField(
        max_length=200,
        label = 'Ciudad:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    descripcion = forms.CharField(
        max_length=200,
        label = 'Descripcion:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '2'
            }
        )
    )

    tipo = forms.ModelChoiceField(
        queryset = Codigos_Maestros.objects.filter(codigo='XXTYPE_ROUTE'),
        label = 'Tipo Recorrido:', 
        initial = 0,
        widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    class Meta:
        model = Evento
        fields = ["nombre", "id_programa", "descripcion",
                  "direccion", "ciudad", "tipo",
                  "unidades_censadas", "km2_recorridos"]
