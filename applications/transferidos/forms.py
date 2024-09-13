from applications.transferidos.models import Programa_Transferidos, Detalle_Transferidos, Archivos_Transferidos, Pagos_Transferidos
import datetime
from django import forms
from applications.home.models import Codigos_Maestros, Oficinas
from applications.users.models import User


class TransferenciaForm(forms.Form):

    lista = forms.CharField(
        required=False,
        widget=forms.HiddenInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    dependencia = forms.ModelChoiceField(
        queryset=Codigos_Maestros.objects.filter(codigo='XXTRANSFER'),
        label='Dependencia:',
        initial=0,
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder': ' '
            }
        )
    )

    comentarios = forms.CharField(
        max_length=200,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'id': 'textarea',
                'class': 'form-control input-area-rec float-label',
                'placeholder' : ' ',
                'rows': '4'
            }
        )
    )


class AceptarForm(forms.Form):

    folio = forms.CharField(
        required=False,
        widget=forms.HiddenInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
class AceptarTodosForm(forms.Form):

    folio = forms.CharField(
        required=False,
        widget=forms.HiddenInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
class RechazarTodosForm(forms.Form):

    folio = forms.CharField(
        required=False,
        widget=forms.HiddenInput(
            attrs={
                'class': 'form-control'
            }
        )
    )


class FechaCierreForm(forms.Form):

    fecha = forms.DateField(
        label='Fecha Seguimiento:',
        required=True,
        initial=datetime.date.today,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control input-rec date-picker-default',
                'placeholder': ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy',
                'data-date-autoclose': 'true'
            }
        )
    )

    comentarios = forms.CharField(
        max_length=200,
        label='Comentarios:',
        required=False,
        widget=forms.Textarea(
            attrs={
                'id': 'textarea',
                'class': 'form-control input-area-rec float-label',
                'placeholder': ' ',
                'rows': '4'
            }
        )
    )


class AsignarAuditoriaForm(forms.Form):

    lista = forms.CharField(
        required=False,
        widget = forms.HiddenInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    seguimiento = forms.ModelChoiceField(
        #queryset = User.objects.filter(groups__name__contains='VIGILANCIA', is_superuser=False),
        #queryset = Codigos_Maestros.objects.filter(codigo='XXASSIGN_AUDITORY'),
        queryset=Oficinas.objects.filter(is_active=True),
        label = 'Seguimiento:', 
        initial=0,
        required=True,
        widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    

class OpcionForm(forms.Form):
    lista = forms.CharField(
        required=False,
        widget=forms.HiddenInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    OPCION = [
        ('ACEPTAR', 'ACEPTAR'),
        ('RECHAZAR', 'RECHAZAR'),
    ]

    opcion = forms.ChoiceField(
        choices=OPCION,
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder': ' '
            }
        )
    )

    comentarios = forms.CharField(
        max_length=200,
        label='Comentarios:',
        required=False,
        widget=forms.Textarea(
            attrs={
                'id': 'textarea',
                'class': 'form-control input-area-rec float-label',
                'placeholder': ' ',
                'rows': '4'
            }
        )
    )

    metodo_envio = forms.ModelChoiceField(
        queryset=Codigos_Maestros.objects.filter(codigo='XXSEND_METHOD').order_by('-id'),
        label='Metodo de Envio:',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder': 'Seleccionar'
            }
        )
    )


class RechazarForm(forms.Form):

    lista = forms.CharField(
        required=False,
        widget=forms.HiddenInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    old_folio = forms.CharField(
        required=False,
        widget=forms.HiddenInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    comentarios = forms.CharField(
        max_length=200,
        label='Comentarios:',
        required=True,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '6'
            }
        )
    )


class BatchForm(forms.Form):

    programa = forms.ModelChoiceField(
        queryset=Codigos_Maestros.objects.filter(codigo='XXTAX').order_by('-id'),
        label='Impuesto:',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    metodo_envio = forms.ModelChoiceField(
        queryset=Codigos_Maestros.objects.filter(codigo='XXSEND_METHOD_EJECUCION').order_by('-id'),
        label='Metodo de Envio:',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    archivo = forms.FileField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept': '.csv'
            }
        )
    )
    

class ContribuyenteEjecucionForm(forms.ModelForm):

    folio = forms.CharField(
        max_length=50,
        label='Folio:',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )

    rfc = forms.CharField(
        max_length=20,
        label='RFC:',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )

    programa = forms.ModelChoiceField(
        queryset=Codigos_Maestros.objects.filter(codigo='XXTAX'),
        label='Impuestos:',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        )
    )

    presuntiva = forms.DecimalField(
        label='Presuntiva:',
        required=True,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )

    nombre = forms.CharField(
        max_length=200,
        label='Nombre:',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )

    direccion = forms.CharField(
        max_length=200,
        label='Domicilio:',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )

    fecha = forms.DateField(
        #label='Fecha:',
        required=True,
        initial=datetime.date.today,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default input-rec float-label',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy',
                'style': 'display:none'
            }
        )
    )
    
    comentarios = forms.CharField(
        max_length=600,
        label='Comentarios:',
        required=False,
        widget=forms.Textarea(
            attrs={
                'id': 'textarea',
                'class': 'form-control input-area-rec float-label',
                'placeholder': ' ',
                'rows': '4'
            }
        )
    )

    metodo_envio = forms.ModelChoiceField(
        queryset=Codigos_Maestros.objects.filter(codigo='XXSEND_METHOD_EJECUCION'),
        label='Metodo de Envio:',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    area = forms.CharField(
        max_length=200,
        label='Area:',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'style': 'display: none'
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
        (2022, '2022'),
    ]

    ejercicio = forms.ChoiceField(
        choices=EJERCICIOS,
        label = 'Ejercicio:',
        initial= 0,
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
        initial= 0,
        required = True,
        widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    class Meta:
        model = Programa_Transferidos
        fields = ["folio", "rfc", "programa",
                  "presuntiva", "nombre", "direccion", 
                  "fecha", "comentarios", "area", 
                  "ejercicio","periodo","metodo_envio"]
                  


class ContribuyenteForm(forms.ModelForm):

    folio = forms.CharField(
        max_length=50,
        label='Folio:',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    rfc = forms.CharField(
        max_length=20,
        label='RFC:',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': ' '
            }
        )
    )

    programa = forms.ModelChoiceField(
        queryset=Codigos_Maestros.objects.filter(codigo='XXTAX'),
        label='Programa:',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder': 'Seleccionar'
            }
        )
    )

    presuntiva = forms.DecimalField(
        label='Presuntiva:',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': ' '
            }
        )
    )

    nombre = forms.CharField(
        max_length=200,
        label='Nombre:',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': ' '
            }
        )
    )

    direccion = forms.CharField(
        max_length=200,
        label='Direccion:',
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': ' '
            }
        )
    )

    fecha = forms.DateField(
        #label='Fecha:',
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
    
    comentarios = forms.CharField(
        max_length=600,
        label='Comentarios:',
        required=False,
        widget=forms.Textarea(
            attrs={
                'id': 'textarea',
                'class': 'form-control input-area-rec float-label',
                'placeholder': ' ',
                'rows': '4'
            }
        )
    )

    metodo_envio = forms.ModelChoiceField(
        queryset=Codigos_Maestros.objects.filter(codigo='XXSEND_METHOD').order_by('-id'),
        label='Metodo de Envio:',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder': 'Seleccionar'
            }
        )
    )
    
    area = forms.CharField(
        max_length=200,
        label='Area:',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'style': 'display: none'
            }
        )
    )

    class Meta:
        model = Programa_Transferidos
        fields = ["folio", "rfc", "programa",
                  "presuntiva", "nombre", "direccion", "fecha", "comentarios", "area", "metodo_envio"]
                  

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
                'id': 'textarea',
                'class': 'form-control input-area-rec float-label',
                'placeholder': ' ',
                'rows': '4'
            }
        )
    )


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
        model = Detalle_Transferidos
        fields = ["folio", "programa_id", "fecha", "comentarios", "etapa", "estatus"]


    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(DetalleForm, self).__init__(*args, **kwargs)
        
        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa_Transferidos.objects.filter(pk=pk), 
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
       queryset = Codigos_Maestros.objects.filter(codigo='XXFILE'),
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
        model = Archivos_Transferidos
        fields = ["folio", "programa_id", "fecha", "tipo","comentarios", "archivo"]

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(ArchivosForm, self).__init__(*args, **kwargs)
        
        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa_Transferidos.objects.filter(pk=pk), 
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
       required=False,
       widget = forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'display:none'
            }
        )
    )

    # folio = forms.CharField(
        # max_length=50,
        # label = 'Folio:',
        # required = False,
        # widget = forms.TextInput(
            # attrs={
                # 'class': 'form-control',
                # 'readonly': 'readonly'
            # }
        # )
    # )

    fecha = forms.DateField(
        label = 'Fecha:',
        required = False,
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
       required = True,
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
        initial = 0,
        widget = forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    recargos = forms.DecimalField(
        label = 'Recargos:',
        required = False,
        initial = 0,
        widget = forms.NumberInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    impuesto = forms.DecimalField(
        label = 'Impuesto:',
        required = False,
        initial = 0,
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
        (2015, '2015'),
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
        initial= 0,
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
        initial= 0,
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
        model = Pagos_Transferidos
        fields = ["programa_id", "presuntiva", "ejercicio", "periodo", "fecha", "tipo", "comentarios", "accesorios", "recargos", "impuesto" ]


    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(PagosForm, self).__init__(*args, **kwargs)
        
        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa_Transferidos.objects.filter(pk=pk), 
            required = False,
            widget = forms.Select(
                attrs={
                    'style': 'display:none'
                }
            )
        )


class ImpuestosForm(forms.Form):

    impuesto = forms.ModelChoiceField(
        queryset=Codigos_Maestros.objects.filter(
            codigo='XXTAX').order_by('-id'),
        label='Impuesto:',
        initial=0,
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder': 'Seleccionar'
            }
        )
    )
