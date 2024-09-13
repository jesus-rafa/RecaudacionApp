import datetime

from django import forms
from django.forms.fields import ChoiceField
from .models import Programa_Padrones, Detalle_Padrones, Archivos_Padrones, Pagos_Padrones
from applications.home.models import Codigos_Maestros
from applications.users.models import User


class TurnarForm(forms.Form):

    lista = forms.CharField(
        required=False,
        widget = forms.HiddenInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    seguimiento = forms.ModelChoiceField(
       queryset = User.objects.filter(groups__name__contains='PADRONES'),
       label = 'Seguimiento:', 
       initial = 0,
       widget = forms.Select(
            attrs={
                'class': 'form-control'

            }
        )
    )



class ProgramacionForm(forms.ModelForm): 
    
    folio = forms.CharField(
        max_length=50,
        label = 'Folio:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    
    rfc = forms.CharField(
        max_length=20,
        label = 'RFC:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    programa = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXPROGRAM_PADRONES'),
       label = 'Programa:',
       initial = 0,
       widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    presuntiva = forms.DecimalField(
        label = 'Presuntiva:',
        required = True,
        widget = forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
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

    direccion = forms.CharField(
        max_length=200,
        label = 'Direccion:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    fecha = forms.DateField(
        label = 'Fecha:',
        required = True,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'value': 'Select Date',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy'
            } 
        )
    )

    # estatus = forms.ModelChoiceField(
    #    queryset = Codigos_Maestros.objects.filter(codigo='XXSTATUS'),
    #    label = 'Etapa:', 
    #    initial = 0,
    #    widget = forms.Select(
    #         attrs={
    #             'class': 'form-control'
    #         }
    #     )
    # )

    estatus = forms.CharField(
        #max_length=200,
        label = 'Etapa:',
        required = False,
        initial='VALIDACION',
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }
        )
    )
    
    seguimiento = forms.ModelChoiceField(
       queryset = User.objects.all(),
       label = 'Seguimiento:', 
       initial = 0,
       widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    class Meta: 
        model = Programa_Padrones
        fields = ["folio", "rfc", "programa", "presuntiva", "nombre", "direccion", "fecha", "seguimiento"]



class DetalleForm(forms.ModelForm):

    programa_id = forms.ModelChoiceField(
       queryset = None,
       label = 'ID:',
       initial = 0,
       required=True,
       widget = forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'display:none'
            }
        )
    )

    folio = forms.CharField(
        max_length=50,
        label = 'Folio:',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }
        )
    )

    fecha = forms.DateField(
        label = 'Fecha:',
        required = True,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'value': 'Select Date',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy'
            } 
        )
    )

    comentarios = forms.CharField(
        max_length=200,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '5'
            }
        )
    )


    # estatus = forms.ModelChoiceField(
       # queryset = Codigos_Maestros.objects.filter(codigo='XXSTATUS_PADRONES'),
       # label = 'Etapa:', 
       # initial = 0,
       # widget = forms.Select(
            # attrs={
                # 'class': 'form-control'
            # }
        # )
    # )
    
    etapa = forms.CharField(
        #queryset =  Codigos_Maestros.objects.filter(codigo='XXSTAGE'),
        #queryset = None,
        label = 'Etapa:', 
        required=False,
        # widget = forms.Select(
        #     attrs={
        #         'class': 'form-control'
        #     }
        # )
    )


    estatus = forms.CharField(
       #queryset =  Codigos_Maestros.objects.filter(codigo='XXSTATUS'),
        #queryset = None,
        label = 'Estatus:', 
        required=False,
        # widget = forms.Select(
        #     attrs={
        #         'class': 'form-control'
        #     }
        # )
    )

    class Meta: 
        model = Detalle_Padrones
        fields = ["folio", "programa_id", "fecha", "comentarios", "etapa", "estatus"]


    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(DetalleForm, self).__init__(*args, **kwargs)
        
        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa_Padrones.objects.filter(pk=pk), 
            required = False,
            widget = forms.Select(
                attrs={
                    'style': 'display:none'
                }
            )
        )


class ArchivosForm(forms.ModelForm):

    # programa_id = forms.FloatField(
    #     label = 'ID:',
    #     required = True,
    #     widget = forms.NumberInput(
    #         attrs={
    #             'class': 'form-control',
    #             'readonly': 'readonly'
    #         }
    #     )
    # )

    programa_id = forms.ModelChoiceField(
       queryset = None,
       label = 'ID:',
       initial = 0,
       required=True,
       widget = forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'display:none'
            }
        )
    )

    folio = forms.CharField(
        max_length=50,
        label = 'Folio:',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }
        )
    )

    fecha = forms.DateField(
        label = 'Fecha:',
        required = True,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'value': 'Select Date',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy'
            } 
        )
    )

    comentarios = forms.CharField(
        max_length=200,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '5'
            }
        )
    )


    tipo = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXFILE_PADRONES'),
       label = 'Tipo:', 
       initial = 0,
       widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    archivo = forms.FileField(required = True)


    class Meta: 
        model = Archivos_Padrones
        fields = ["folio", "programa_id", "fecha", "tipo","comentarios", "archivo"]

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(ArchivosForm, self).__init__(*args, **kwargs)
        
        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa_Padrones.objects.filter(pk=pk), 
            required = False,
            widget = forms.Select(
                attrs={
                    'style': 'display:none'
                }
            )
        )


class PagosForm(forms.ModelForm):

    programa_id = forms.ModelChoiceField(
       queryset = None,
       label = 'ID:',
       initial = 0,
       required=True,
       widget = forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'display:none'
            }
        )
    )

    folio = forms.CharField(
        max_length=50,
        label = 'Folio:',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }
        )
    )

    fecha = forms.DateField(
        label = 'Fecha:',
        required = True,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'value': 'Select Date',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy'
            } 
        )
    )

    comentarios = forms.CharField(
        max_length=200,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '5'
            }
        )
    )

    tipo = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXTAX'),
       label = 'Tipo:', 
       initial = 0,
       widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    accesorios = forms.DecimalField(
        label = 'Accesorios:',
        required = False,
        initial=0,
        widget = forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    recargos = forms.DecimalField(
        label = 'Recargos:',
        required = False,
        initial=0,
        widget = forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    impuesto = forms.DecimalField(
        label = 'Impuesto:',
        required = True,
        initial=0,
        widget = forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    PERIODOS = [
        (1, 'ENE'),
        (2, 'FEB'),
        (3, 'MAR'),
        (4, 'ABR'),
        (5, 'MAY'),
        (6, 'JUN'),
        (7, 'JUL'),
        (8, 'AGO'),
        (9, 'SEP'),
        (10, 'OCT'),
        (11, 'NOV'),
        (12, 'DIC'),
    ]

    EJERCICIOS = [
        (2016, '2016'),
        (2017, '2017'),
        (2018, '2018'),
        (2019, '2019'),
        (2020, '2020'),
        (2021, '2021'),
    ]

    ejercicio = forms.ChoiceField(
        choices=EJERCICIOS,
        label = 'Ejercicio:',
        required = True,
        widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    periodo = forms.ChoiceField(
        choices=PERIODOS,
        label = 'Periodo:',
        required = True,
        widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    presuntiva = forms.BooleanField(
        label = 'Presuntiva:',
        initial=True,
        required = False,
        widget = forms.CheckboxInput(
            attrs={
                'class': ''
            }
        )
    )

    class Meta: 
        model = Pagos_Padrones
        fields = ["folio", "programa_id", "presuntiva", "ejercicio", "periodo", "fecha", "tipo", "comentarios", "accesorios", "recargos", "impuesto" ]


    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(PagosForm, self).__init__(*args, **kwargs)
        
        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa_Padrones.objects.filter(pk=pk), 
            required = False,
            widget = forms.Select(
                attrs={
                    'style': 'display:none'
                }
            )
        )