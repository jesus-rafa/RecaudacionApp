import datetime
from django import forms
from .models import Contacto, REC
from applications.programacion.models import Programa
from applications.home.models import Codigos_Maestros
from django.contrib.auth import get_user_model

User = get_user_model()

class ContactoForm(forms.ModelForm): 
    
    rfc = forms.ModelChoiceField(
        queryset = None,
        label = 'RFC:',
        required = True,
        widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    # programa_id = forms.ModelChoiceField(
       # queryset = Programa.objects.all(),
       # label = 'ID:',
       # initial = 0,
       # required=False,
       # widget = forms.Select(
            # attrs={
                # 'class': 'form-control',
                # 'style': 'display:none'
            # }
        # )
    # )

    correo = forms.EmailField(
       label = 'Correo:',
       required = False,
       widget = forms.EmailInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    telefono = forms.CharField(
        label = 'Telefono:',
        max_length=20,
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    ext = forms.CharField(
        label = 'Extencion:',
        max_length=10,
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    nombre = forms.CharField(
        max_length=200,
        label = 'Nombre:',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    puesto = forms.ModelChoiceField(
        queryset = Codigos_Maestros.objects.filter(codigo='XXJOB'),
        label = 'Puesto:',
        required = False,
        widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    # puesto = forms.CharField(
    #     max_length=200,
    #     label = 'Puesto:',
    #     required = False,
    #     widget = forms.TextInput(
    #         attrs={
    #             'class': 'form-control'
    #         }
    #     )
    # )

    direccion = forms.CharField(
        max_length=254,
        label = 'Direccion:',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    
    fecha_alta = forms.DateField(
        label = 'Fecha Alta:',
        required = True,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'value': 'Select Date',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy',
                'data-date-autoclose':'true'
            } 
        )
    )


    imagen = forms.ImageField(required = False)

    coordenadas = forms.CharField(
        #max_length=200,
        label = 'Coordenadas:',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    actualizado = forms.BooleanField(
        label = 'Actualizado en REC:',
        initial=False,
        required = False,
        widget = forms.CheckboxInput(
            attrs={
                'class': ''
            }
        )
    )



    class Meta: 
        model = Contacto
        fields = ["rfc", "actualizado", "direccion", "correo", "puesto", "telefono", "ext", "nombre", "fecha_alta", "imagen", "coordenadas"]
        
    def __init__(self, rfc, *args, **kwargs):
        self.rfc = rfc

        super(ContactoForm, self).__init__(*args, **kwargs)
        
        self.fields['rfc'] = forms.ModelChoiceField(
            queryset=REC.objects.filter(rfc=rfc), 
            required = False
        )


class BatchForm(forms.Form):
    archivo = forms.FileField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept': '.csv'
            }
        )
    )
