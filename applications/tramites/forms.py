import datetime

from django import forms
from .models import NuevoTramite,Tipos,Tramite,Estatus
from django.forms import ModelForm
from ckeditor.widgets import CKEditorWidget



class FormNuevoTramite(forms.ModelForm):

    confianza = forms.BooleanField(
        label='Confianza',
        required = False,
        widget = forms.CheckboxInput(
            attrs={
                 
                'class':'form-check-input rounded-circle'
            }
        ),

        
    )


    honorarios = forms.BooleanField(
        label='Honorarios',
        # initial=True,
        required=False,
        
        widget=forms.CheckboxInput(
            attrs={
                
                 'class':'form-check-input rounded-circle'
            }
        )
    )

    plaza = forms.BooleanField(
        label='Base',
        # initial=True,
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                'class':'form-check-input rounded-circle'
                # 'data-plugin': 'switchery',
                # 'data-color': '#363636',
                # 'data-size': 'small'
            }
        )
    )

    

    tramite = forms.ModelChoiceField(
        queryset=Tramite.objects.all(),
        label = 'Trámite',
        initial = 0,
        widget = forms.Select(
            attrs = {
                'class' : 'form-control selectize-select selectized',
                'placeholder': 'Seleccionar'
                
            }
        )

    )

    estatus = forms.ModelChoiceField(
        queryset=Estatus.objects.all(),
        label = 'Estatus',
        initial = 4,
        required=False,
        widget = forms.Select(
            attrs = {
                'class' : 'form-control input-rec',
                'placeholder': 'Tramite'
                
            }
        )

    )
    
    tipo = forms.ModelChoiceField(
        queryset=Tipos.objects.all(),
        label='Tipo',
        initial=0,
        widget = forms.Select(
            attrs={
                'class' : 'form-control selectize-select selectized',
                'placeholder': 'Seleccionar'
            }
        )
    )

    servicio = forms.CharField(
        max_length=50,
        label='Nombre Tramite',
        required=False,
        widget = forms.TextInput(
            attrs={
                'class' : 'form-control input-rec',
                'placeholder': 'Tramite'
            }
        )
    )

    titulo_formato = forms.CharField(
        required=False,
        widget=CKEditorWidget(
            attrs={
                'class' : 'mx-auto',
                
            }
        )
    )

    comentarios = forms.CharField(
        max_length=100,
        label='Nombre Tramite',
        required=False,
        widget = forms.TextInput(
            attrs={
                'class' : 'form-control input-rec',
                'placeholder': ''
            }
        )
    )

    is_active = forms.BooleanField(
        label='Activo',
        required = False,
        widget = forms.CheckboxInput(
            attrs={
                
                'class':'form-check-input rounded-circle'
            }
        ),

    
    )




    class Meta: 
        model = NuevoTramite 
        fields = ["honorarios", "plaza", "tipo","servicio","titulo_formato","confianza",'tramite','estatus','comentarios','is_active']





    
