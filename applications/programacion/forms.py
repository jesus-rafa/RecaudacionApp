import datetime
from operator import itemgetter
from django import forms
from django.forms.fields import ChoiceField
from .models import Programa, Detalle, Archivos, Pagos, Contribuyentes, Archivos_Contribuyente
from applications.home.models import Codigos_Maestros
from applications.users.models import User
from django.db.models import Q


class ContribuyentesForm(forms.Form): 
    rfc = forms.CharField(
        label = 'RFC:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'style': 'display:none'
            }
        )
    )

    programa = forms.CharField(
        label = 'Programa:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'style': 'display:none'
            }
        )
    )


class ImpuestosForm(forms.Form): 

    impuesto = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXTAX').order_by('-id'),
       label = 'Impuesto:',
       initial = 0,
       required=True,
       widget = forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : 'Seleccionar'
            }
        )
    )


class CerrarAnalisisForm(forms.Form): 

    monto = forms.DecimalField(
        label = 'Monto:',
        required = False,
        widget = forms.NumberInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )

    comentarios = forms.CharField(
        max_length=200,
        label = 'Comentarios:',
        required = True,
        widget = forms.Textarea(
            attrs={
                'id': 'textarea',
                'class': 'form-control input-area-rec float-label',
                'placeholder' : ' ',
                'rows': '4'
            }
        )
    )

    estatus = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXTAKE_TAXPAYERS'),
       label = 'Estatus:',
       initial = 0,
       required=True,
       widget = forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'onChange': 'mostrarMotivo(this)',
                'placeholder' : ' '
            }
        )
    )
    
    motivo = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXREASON'),
       label = 'Motivo:',
       initial = 0,
       required=True,
       widget = forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : ' ',
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
       queryset = Codigos_Maestros.objects.filter(codigo='XXPROGRAM'),
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
                'format': 'dd/mm/yyyy',
                'data-date-autoclose':'true'
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
        model = Programa
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
                'class': 'form-control input-rec date-picker-default',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy',
                'data-date-autoclose':'true'
            } 
        )
    )

    comentarios = forms.CharField(
        max_length=600,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'id': 'textarea',
                'class': 'form-control input-area-rec float-label',
                'placeholder' : ' ',
                'rows': '5'
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
        model = Detalle
        fields = ["folio", "programa_id", "fecha", "comentarios", "etapa", "estatus"]


    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(DetalleForm, self).__init__(*args, **kwargs)
        
        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa.objects.filter(pk=pk), 
            required = False,
            widget = forms.Select(
                attrs={
                    'style': 'display:none'
                }
            )
        )


class ArchivosSolicitudForm(forms.ModelForm):

    programa_id = forms.ModelChoiceField(
        queryset=None,
        label='ID:',
        initial=0,
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'display:none'
            }
        )
    )

    folio = forms.CharField(
        max_length=50,
        label='Folio:',
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            }
        )
    )

    fecha = forms.DateField(
        label='Fecha:',
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
                'class': 'form-control',
                'style': 'display:none',
                'rows': '5'
            }
        )
    )


    tipo = forms.ModelChoiceField(
        queryset=Codigos_Maestros.objects.filter(codigo='XXFILE_TICKET'),
        label='Tipo:',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder': ' ',
            }
        )
    )

    archivo = forms.FileField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    class Meta:
        model = Archivos
        fields = ["folio", "programa_id", "fecha",
                  "tipo", "comentarios", "archivo"]

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(ArchivosSolicitudForm, self).__init__(*args, **kwargs)

        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa.objects.filter(pk=pk),
            required=False,
            widget=forms.Select(
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
                'format': 'dd/mm/yyyy',
                'data-date-autoclose':'true'
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
        model = Archivos
        fields = ["folio", "programa_id", "fecha", "tipo","comentarios", "archivo"]

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(ArchivosForm, self).__init__(*args, **kwargs)
        
        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa.objects.filter(pk=pk), 
            required = False,
            widget = forms.Select(
                attrs={
                    'style': 'display:none'
                }
            )
        )



class ArchivosForm2(forms.ModelForm):

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
                'format': 'dd/mm/yyyy',
                'data-date-autoclose':'true'
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
        queryset = Codigos_Maestros.objects.filter(
            comentario__in=['CONSTANCIA DE ENTREGA DE OFICIO INVITACION', 'CONSTANCIA DE NO ENTREGA DE OFICIO INVITACION']
        ),
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
        model = Archivos
        fields = ["folio", "programa_id", "fecha", "tipo","comentarios", "archivo"]

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(ArchivosForm2, self).__init__(*args, **kwargs)
        
        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa.objects.filter(pk=pk), 
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
                'class': 'form-control input-rec date-picker-default',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy',
                'data-date-autoclose':'true'
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
                'class': 'form-control selectize-select',
                'placeholder' : ' '
            }
        )
    )

    accesorios = forms.DecimalField(
        label = 'Accesorios:',
        required = False,
        #initial = 0,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder' : ' '
            }
        )
    )

    recargos = forms.DecimalField(
        label = 'Recargos:',
        required = False,
        #initial = 0,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder' : ' '
            }
        )
    )

    impuesto = forms.DecimalField(
        label = 'Impuesto:',
        required = False,
        #initial = 0,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder' : ' '
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
        (2023, '2023'),
        (2022, '2022'),
        (2021, '2021'),
        (2020, '2020'),
        (2019, '2019'),
        (2018, '2018'),
        (2017, '2017'),
        # (2016, '2016'),
    ]

    ejercicio = forms.ChoiceField(
        choices=sorted(EJERCICIOS, key=itemgetter(0)),
        label = 'Ejercicio:',
        required = True,
        widget = forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : ''
            }
        )
    )

    periodo = forms.ChoiceField(
        choices=sorted(PERIODOS, key=itemgetter(0)),
        label = 'Periodo:',
        required = True,
        widget = forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : ''
            }
        )
    )
    
    presuntiva = forms.BooleanField(
        label = 'Presuntiva:',
        #initial=True,
        required = False,
        widget = forms.CheckboxInput(
            attrs={
                'data-plugin': 'switchery',
                'data-color': '#363636',
                'data-size': 'small'
            }
        )
    )

    class Meta: 
        model = Pagos
        fields = ["folio", "programa_id", "presuntiva", "ejercicio", "periodo", "fecha", "tipo", "comentarios", "accesorios", "recargos", "impuesto" ]


    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(PagosForm, self).__init__(*args, **kwargs)
        
        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa.objects.filter(pk=pk), 
            required = False,
            widget = forms.Select(
                attrs={
                    'style': 'display:none'
                }
            )
        )
        
        
class ContribuyenteForm(forms.ModelForm): 
    
    folio = forms.CharField(
        max_length=50,
        label = 'Folio:',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder' : ' '

            }
        )
    )

    # rfc = forms.ModelChoiceField(
    #    queryset = None,
    #    label = 'RFC:',
    #    initial = 0,
    #    #required=True,
    #    widget = forms.Select(
    #         attrs={
    #             'class': 'form-control',
    #         }
    #     )
    # )
    
    rfc = forms.CharField(
        max_length=20,
        label = 'RFC',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder' : ' '
            }
        )
    )

    programa = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXPROGRAM'),
       label = 'Programa',
       initial = 0,
       required=True,
       widget = forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : ' '
            }
        )
    )
    
    presuntiva = forms.DecimalField(
        label = 'Presuntiva',
        required = False,
        widget = forms.NumberInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder' : ' '
            }
        )
    )
    
    nombre = forms.CharField(
        max_length=200,
        label = 'Nombre',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder' : ' '
            }
        )
    )

    direccion = forms.CharField(
        max_length=200,
        label = 'Direccion',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder' : ' '
            }
        )
    )
    
    interlocutor = forms.CharField(
        max_length=10,
        label = 'Interlocutor',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder' : ' '
            }
        )
    )
    
    fecha = forms.DateField(
        label = 'Fecha',
        required = False,
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


    class Meta: 
        model = Programa
        fields = ["folio", "rfc", "programa", "presuntiva", "nombre", "direccion", "fecha", "interlocutor"]

    
    # def __init__(self, *args, **kwargs):
    #     username = kwargs.pop('username', '')
    #     is_ready = kwargs.pop('is_ready', False)

    #     super(ContribuyenteForm, self).__init__(*args, **kwargs)
        
    #     self.fields['rfc'] = forms.ModelChoiceField(
    #         label = 'RFC:',
    #         queryset=Contribuyentes.objects.filter(usuario=username,estatus='PROCEDENTE',is_ready=is_ready).order_by('prioridad'),
    #         required = True,
    #         initial = 0,
    #         widget = forms.Select(
    #             attrs={
    #                 'class': 'form-control selectize-select',
    #             }
    #         )
    #     )
        


class CerrarApoyoForm(forms.Form):
    
    comentarios = forms.CharField(
        max_length=600,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': '5'
            }
        )
    )


class AsignarForm(forms.Form):

    lista = forms.CharField(
        required=False,
        widget = forms.HiddenInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    seguimiento = forms.ModelChoiceField(
        queryset = User.objects.filter(groups__name__contains='JEFE COBRO', is_superuser=False, is_active=True),
        label = 'Asignar a:', 
        initial=0,
        required=True,
        widget = forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : 'Seleccionar'
            }
        )
    )
    
    observaciones = forms.CharField(
        max_length=600,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'id': 'textarea',
                'class': 'form-control input-area-rec float-label',
                'placeholder' : ' ',
                'rows': '2'
            }
        )
    )
    
class SolicitarForm(forms.ModelForm):

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

    fecha = forms.DateField(
        label = 'Fecha:',
        required = True,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'value': 'Select Date',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy',
                'style': 'display:none'
            } 
        )
    )

    class Meta: 
        model = Detalle
        fields = ["programa_id", "fecha"]


    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(SolicitarForm, self).__init__(*args, **kwargs)
        
        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa.objects.filter(pk=pk), 
            required = False,
            widget = forms.Select(
                attrs={
                    'style': 'display:none'
                }
            )
        )

        
class CierreForm(forms.ModelForm):

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

    fecha = forms.DateField(
        label = 'Fecha:',
        required = True,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'value': 'Select Date',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy',
                'style': 'display:none'
            } 
        )
    )

    
    comentarios_area = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXTRANSFER'),
       label = 'Area:',
       required=False,
       widget = forms.Select(
            attrs={
                'class': 'form-control',
                'style': 'display:none'
                
            }
        )
    )
    
    estatus = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXSTATUS', comentario__in=['CONCLUIDO', 'PROPUESTA TRANSFERENCIA', 'SOLICITUD CONCLUIDA']),
       label = 'ID:',
       initial = 0,
       required=True,
       widget = forms.Select(
            attrs={
                'class': 'form-control change_estatus'
                
            }
        )
    )

    class Meta: 
        model = Detalle
        fields = ["programa_id", "fecha", "comentarios_area", "estatus"]


    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(CierreForm, self).__init__(*args, **kwargs)
        
        self.fields['programa_id'] = forms.ModelChoiceField(
            queryset=Programa.objects.filter(pk=pk), 
            required = False,
            widget = forms.Select(
                attrs={
                    'style': 'display:none'
                }
            )
        )

    
class ReasignarForm(forms.Form):

    lista = forms.CharField(
        required=False,
        widget = forms.HiddenInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    seguimiento = forms.ModelChoiceField(
        queryset = User.objects.filter(groups__name__contains='JEFE COBRO', is_superuser=False, is_active=True),
        label = 'Seguimiento:', 
        initial=0,
        required=True,
        widget = forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : ' '
            }
        )
    )

class CerrarRFCForm(forms.Form):

    cerrar = forms.BooleanField(
        label = 'Cerrar',
        required = False,
        widget = forms.CheckboxInput(
            attrs={
                'class': '',
                'data-plugin': 'switchery',
                'data-color': '#1bb99a'
                # 'checked': 'checked'
            }
        )
    )

    reactivar = forms.BooleanField(
        label = 'Reactivar',
        required = False,
        widget = forms.CheckboxInput(
            attrs={
                'class': '',
                'data-plugin': 'switchery',
                'data-color': '#1bb99a'  
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
                'rows': '3'
            }
        )
    )


class EstatusCierre(forms.Form):

    estatus = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXSTATUS', comentario__in=['CONCLUIDO', 'PROPUESTA TRANSFERENCIA', 'SOLICITUD CONCLUIDA']),
       label = 'Estatus:',
       initial = 0,
       required=True,
       widget = forms.Select(
            attrs={
                'class': 'form-control',
                'style' : 'display: none'
            }
        )
    )

    estatus_cierre = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXSTATUSCIERRE').order_by('-id'),
       label = 'Motivo:',
       initial = 0,
       required=True,
       widget = forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : 'Seleccionar'
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
 
class Archivos_Contribuyente_Form(forms.ModelForm):

    contribuyente = forms.ModelChoiceField(
       queryset = None,
       required=True,
       widget = forms.Select(
            attrs={
                #'style': 'display:none'
            }
        )
    )

    tipo = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXFILE'),
       label = 'Tipo:', 
       initial = 0,
       widget = forms.Select(
            attrs={
                'class': 'form-control selectize-select'
            }
        )
    )

    fecha = forms.DateField(
        label = 'Fecha:',
        required = True,
        initial=datetime.date.today,
        widget = forms.DateInput(attrs={
                'class': 'form-control input-rec date-picker-default',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy',
                
                # 'class': 'form-control date-picker-default',
                # 'value': 'Select Date',
                # 'readonly': 'readonly',
                # 'format': 'dd/mm/yyyy',
                'data-date-autoclose':'true'
            } 
        )
    )

    comentarios = forms.CharField(
        max_length=200,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'class': 'form-control input-rec',
                'rows': '5'
            }
        )
    )

    archivo = forms.FileField(
        required = False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    class Meta: 
        model = Archivos_Contribuyente
        fields = ["contribuyente", "tipo", "fecha", "comentarios", "archivo"]

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk', 0)

        super(Archivos_Contribuyente_Form, self).__init__(*args, **kwargs)
        
        self.fields['contribuyente'] = forms.ModelChoiceField(
            queryset=Contribuyentes.objects.filter(pk=pk), 
            required = True,
            widget = forms.Select(
                attrs={
                    'style': 'display:none'
                    #'class': 'form-control selectize-select',
                }
            )
        )
