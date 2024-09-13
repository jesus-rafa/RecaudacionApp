from django import forms
from django.db.models import Q
from applications.home.models import Municipio
import datetime

from applications.juridico.models import Catalogo, Demanda, Rubros, Solicitante, Resolutor, Resolutor_detalle, Requisitos
from applications.users.models import User

class Form_Demanda(forms.ModelForm):
    juicio = forms.ModelChoiceField(
        queryset = Catalogo.objects.filter(Q(agrupador= 'SELECT_JUICIO') ),
        label='Juicio',
        initial=0,
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'selectize-select sin-borde',
                'placeholder' : 'Tipo juicio',
                'onChange': 'tipojuicio(this)',                
            }
        )
    )
    carpeta = forms.CharField(
        max_length=100,
        label = 'Carpeta',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    subtipo = forms.ModelChoiceField(
        queryset=Catalogo.objects.filter(Q(agrupador='SELECT_SUBTIPO')),
        label='Subtipo',
        initial=0,
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : 'Subtipo juicio',
                'onChange': 'tipo_computo(this)',
            }
        )
    )
    expediente = forms.CharField(
        max_length=100,
        label = 'Expediente',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',

            }
        )
    )
    tribunal = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador = 'SELECT_TRIBUNAL')),
        label='Tribunal',
        initial=0,
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : 'Tribunal',
            }
        )
    )
    fecha_aviso = forms.DateField(
        label='Fecha aviso',
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control input-rec date-picker-default',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy'
            }
        )
    )
    fecha_notificacion = forms.DateField(
        label='Fecha notificacion',
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control input-rec date-picker-default',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy'
            }
        )
    )
    fecha_fatal = forms.DateField(
        label='Fecha fatal',
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control input-rec date-picker-default',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy'
            }
        )
    )
    fecha_interno = forms.DateField(
        label='Fecha interno',
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control input-rec date-picker-default',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy'
            }
        )
    )
    dictaminador = forms.ModelChoiceField(
        queryset= User.objects.filter(areas_id = 4, groups__name__contains='Dictaminador'),    
        label='Abogado',
        initial=0,
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : 'Abogado dictaminador',
            }
        )
    )
    estado_procesal = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(agrupador = 'ESTADO_PROCESAL', sort = 1),
        label='Estado',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'selectize-select sin-borde'
            }
        )
    )
    autoridad = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_AUTORIDAD')),
        label='Autoridad',
        initial=0,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : 'Autoridad',
            }
        )
    )
    resolucion_impg = forms.CharField(
        max_length=100,
        label = 'Resolucion impugnada',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    cuantia = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        label = 'Cuantia',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'onChange': 'validaCampo(this)',
                'placeholder' : ' ',
            }
        )
    )
    materia = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_MATERIA')),
        label='Materia',
        initial=0,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : 'Materia',
            }
        )
    )
    contribuyente = forms.CharField(
        max_length=100,
        label = 'Contribuyente',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    rfc  = forms.CharField(        
        label = 'RFC',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'style': "text-transform:uppercase",
            }
        )
    )
    abogado_prom = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_PROMOVENTE')),
        label='Abogado_Prom',
        initial=0,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : 'Abogado promovente',
            }
        )
    )
    fecha_resolucion = forms.DateField(
        label='fecha_resolucion',
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default input-rec float-label',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy'
            }
        )
    )
    resolucion_rec  = forms.CharField(
        max_length=100,
        required=False,
        label = 'Resolucion recurrida',
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    autoridad_rec = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_AUTORIDAD')),
        label='Autoridad_Rec',
        initial=0,
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : 'Autoridad recurrida',
            }
        )
    )

    class Meta: 
        model = Demanda
        fields = ['juicio','carpeta','subtipo','expediente','tribunal','fecha_aviso','fecha_notificacion','fecha_fatal','fecha_interno',
                    'dictaminador', 'estado_procesal', 'autoridad', 'resolucion_impg','cuantia','materia', 'contribuyente','rfc', 'abogado_prom',
                    'fecha_resolucion','resolucion_rec', 'autoridad_rec']

"""" FORMULARIO EDITA DEMANDA """
class Form_Edita_Demanda(forms.ModelForm):
    #SE AGREGAN NUEVO FORMATO #
    juicio = forms.ModelChoiceField(
        queryset = Catalogo.objects.filter(Q(agrupador= 'SELECT_JUICIO') ),
        label='Juicio',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'selectize-select sin-borde',
                'placeholder' : ' ',
                'onChange': 'tipojuicio(this)',
            }
        )
    )
    # carpeta = forms.CharField(
    #     max_length=100,
    #     label = 'Carpeta',
    #     required = False,
    #     widget = forms.TextInput(
    #         attrs={
    #             'class': 'form-control'
    #         }
    #     )
    # )
    subtipo = forms.ModelChoiceField(
        queryset=Catalogo.objects.filter(Q(agrupador='SELECT_SUBTIPO')),
        label='Subtipo',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select'
                ,'onChange': 'tipo_computo(this)'
            }
        )
    )
    expediente = forms.CharField(
        max_length=100,
        label = 'Expediente',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    tribunal = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador = 'SELECT_TRIBUNAL')),
        label='Tribunal',
        required=False,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : 'Tribunal',
            }
        )
    )
    fecha_aviso = forms.DateField(
        label='Fecha aviso',
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control input-rec date-picker-default',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy'
            }
        )
    )
    fecha_notificacion = forms.DateField(
        label='Fecha notificacion',
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control input-rec date-picker-default',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy'
            }
        )
    )
    fecha_fatal = forms.DateField(
        label='Fecha fatal',
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control input-rec date-picker-default',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy'
            }
        )
    )
    fecha_interno = forms.DateField(
        label='Fecha interno',
        required=True,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control input-rec date-picker-default',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy'
            }
        )
    )
    dictaminador = forms.ModelChoiceField(
        queryset= User.objects.filter(areas_id = 4, groups__name__contains='Dictaminador'),   
        label='Abogado',
        required=False,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select',
                'placeholder' : 'Abogado dictaminador',
            }
        )
    )   
    estado_procesal = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(agrupador = 'ESTADO_PROCESAL', sort = 1),
        label='Estado',
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'selectize-select sin-borde',
                'placeholder' : ' ',
            }
        )
    )
    autoridad = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_AUTORIDAD')),
        label='Autoridad',
        required = False,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select'
            }
        )
    )
    resolucion_impg = forms.CharField(
        max_length=100,
        label = 'Resolucion impugnada',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    cuantia = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        label = 'Cuantia',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                #'data-currency-symbol': '$',
                #'maxlength': '15',
                'onChange': 'validaCampo(this)',
                'placeholder' : ' ',
            }
        )
    )
    materia = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_MATERIA')),
        label='Materia',
        required = False,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select'
            }
        )
    )
    contribuyente = forms.CharField(
        max_length=100,
        label = 'Contribuyente',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    rfc  = forms.CharField(        
        label = 'RFC',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'style': "text-transform:uppercase",
            }
        )
    )
    abogado_prom = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_PROMOVENTE')),
        label='Abogado_Prom',
        required = False,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select'
            }
        )
    )
    fecha_resolucion = forms.DateField(
        label='fecha_resolucion',
        required=False,
        initial=datetime.date.today,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default input-rec float-label',
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy'
            }
        )
    )
    resolucion_rec  = forms.CharField(
        max_length=100,
        required=False,
        label = 'Resolucion recurrida',
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    autoridad_rec = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_AUTORIDAD')),
        label='Autoridad_Rec',
        initial=0,
        required = False,       
        widget=forms.Select(
            attrs={
                'class': 'form-control selectize-select'
            }
        )
    )

    # fecha_contestacion = forms.DateField(
    #     label='Contestacion:',
    #     required = False,
    #     widget=forms.DateInput(
    #         attrs={
    #             'class': 'form-control date-picker-default input-rec float-label',
    #             'placeholder' : ' ',
    #             'readonly': 'readonly',                
    #             'data-date-format': 'dd/mm/yyyy'
    #         }
    #     )
    # )
    # oficio = forms.CharField(
    #     max_length=100,
    #     label = 'Oficio:',
    #     required = False,
    #     widget = forms.TextInput(
    #         attrs={
    #             'class': 'form-control input-rec float-label',
    #             'placeholder' : ' ',
    #         }
    #     )
    # )

    class Meta: 
        model = Demanda
        fields = ['juicio','subtipo','expediente','tribunal','fecha_aviso','fecha_notificacion','fecha_fatal','fecha_interno',
                    'dictaminador', 'estado_procesal', 'autoridad', 'resolucion_impg','cuantia','materia', 'contribuyente','rfc', 'abogado_prom',
                    'fecha_resolucion','resolucion_rec', 'autoridad_rec']

class Form_Solicitante(forms.ModelForm):
    rfc = forms.CharField(        
        label = 'RFC',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'style': "text-transform:uppercase",
                'v-model':"kword"
            }
        )
    )
    nombre = forms.CharField(        
        label = 'Nombre',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'v-model':"nombre"
            }
        )
    )
    apeP = forms.CharField(        
        label = 'Apellido Paterno',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'v-model':"apeP"
            }
        )
    )
    apeM = forms.CharField(        
        label = 'Apellido Materno',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'v-model':"apeM"
            }
        )
    )
    calle = forms.CharField(        
        label = 'Calle',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'v-model':"direccion"
            }
        )
    )
    numero = forms.IntegerField(
        required = True,
        label = 'Numero',
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'v-model':"numero"
            }
        )
    )
    colonia = forms.CharField(        
        label = 'Colonia',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'v-model':"colonia"
            }
        )
    )
    ciudad = forms.CharField(        
        label = 'Ciudad',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'v-model':"ciudad"
            }
        )
    )
    cp = forms.CharField(        
        label = 'Codigo postal',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'v-model':"cp"
            }
        )
    )
    telefono = forms.IntegerField(
        required = True,
        label = 'Telefono',
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'v-model':"telefono"
            }
        )
    )

    class Meta: 
        model = Solicitante
        fields = ['rfc','nombre','apeP','apeM','calle','numero','colonia','ciudad','cp','telefono']

class Form_Resolutor(forms.ModelForm):
    carpeta = forms.CharField(      
        label = 'Expediente y/o carpeta',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    oficio = forms.CharField(        
        label = 'Oficio',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    fecha_presentacion = forms.DateField(
        label='Fecha presentacion',
        required=False,   
        initial=datetime.date.today,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default input-rec float-label',                
                'placeholder' : ' ',
                'readonly': 'readonly',
                'data-date-format': 'dd/mm/yyyy'
            }
        )
    )
    
    # fecha_resolucion = forms.DateField(
    #     label='Fecha resolucion',
    #     required=False,
    #     initial=datetime.date.today,
    #     widget=forms.DateInput(
    #         attrs={
    #             'class': 'form-control date-picker-default input-rec float-label',                
    #             'placeholder' : ' ',
    #             'readonly': 'readonly',
    #             'data-date-format': 'dd/mm/yyyy'
    #         }
    #     )
    # )
    concepto =  forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_FORMATO')),
        label='Concepto',
        required = False,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'selectize-select sin-borde',
                'placeholder' : 'Concepto',
            }
        )
    )
    solicitante =  forms.ModelChoiceField(
        queryset= Solicitante.objects.all(),
        #to_field_name="rfc",
        label='RFC solicitante',
        required = False,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'selectize-select sin-borde',
                'placeholder' : 'RFC solicitante',
            }
        )
    )
    ejercicio_ini = forms.IntegerField(
        required=False,
        label = 'Ejecicio inicio',
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    ejercicio_fin = forms.IntegerField(
        required=False,
        label = 'Ejecicio fin',
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    # caducidad = forms.ModelChoiceField(
    #     queryset= Catalogo.objects.filter(Q(agrupador='SELECT_PROMOVENTE')),
    #     label='Caducidad',
    #     required = False,
    #     initial=0,
    #     widget=forms.Select(
    #         attrs={
    #             'class': 'selectize-select sin-borde',
    #             'placeholder' : 'Caducidad',
                
    #         }
    #     )
    # )
    marca = forms.CharField(        
        label = 'Marca',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    modelo = forms.CharField(        
        label = 'Modelo',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    serie = forms.CharField(        
        label = 'Serie',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    placa = forms.CharField(        
        label = 'Placa',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    documentacion = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_DOCUMENTACION')),
        label='Documentacion',
        required = False,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'selectize-select sin-borde',
                'placeholder' : 'Documentacion',
            }
        )
    )
    # sentido = forms.ModelChoiceField(
    #     queryset= Catalogo.objects.filter(Q(agrupador='SELECT_SENTIDO_RESOLUTOR')),
    #     label='Sentido',
    #     required = False,
    #     initial=0,
    #     widget=forms.Select(
    #         attrs={
    #             'class': 'selectize-select sin-borde',
    #             'placeholder' : 'Sentido',
    #         }
    #     )
    # )
    # formato = forms.ModelChoiceField(
    #     queryset= Catalogo.objects.filter(Q(agrupador='SELECT_FORMATO')),
    #     label='Formato',
    #     required = False,
    #     initial=0,
    #     widget=forms.Select(
    #         attrs={
    #             'class': 'selectize-select sin-borde',
    #             'placeholder' : 'Formato',
    #         }
    #     )
    # )
    # fecha_notificacion = forms.DateField(
    #     label='Fecha notificacion',
    #     required=False,
    #     initial=datetime.date.today,
    #     widget=forms.DateInput(
    #         attrs={
    #             'class': 'form-control date-picker-default input-rec float-label',                
    #             'placeholder' : ' ',
    #             'readonly': 'readonly',
    #             'data-date-format': 'dd/mm/yyyy'
    #         }
    #     )
    # )
    titular = forms.ModelChoiceField(
        queryset= User.objects.all(),
        label='Titular',
        required = False,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'selectize-select sin-borde',
                'placeholder' : 'Titular',

            }
        )
    )
    municipio = forms.ModelChoiceField(
        #queryset= Catalogo.objects.filter(Q(agrupador='SELECT_PROMOVENTE')),
        queryset= Municipio.objects.filter(Q(estado_id=11)),
        label='Municipio',
        required = False,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'selectize-select sin-borde',
                'placeholder' : 'Municipio',
            }
        )
    )
    # abogado = forms.ModelChoiceField(
    #     queryset= User.objects.filter(areas_id = 4, groups__name__contains='Dictaminador'),    
    #     label='Abogado',
    #     initial=0,
    #     required=True,
    #     widget=forms.Select(
    #         attrs={
    #             'class': 'selectize-select sin-borde',
    #             'placeholder' : 'Abogado',
    #         }
    #     )
    # )
   
    class Meta: 
        model = Resolutor
        fields = ['carpeta','oficio','fecha_presentacion','concepto',"solicitante",'ejercicio_ini','ejercicio_fin','marca','modelo','serie','placa','documentacion','titular','municipio']
            
class Form_ResolutorDetalle(forms.ModelForm):
    comentarios = forms.CharField(      
        label = 'Comentarios',
        #required = True,
        widget = forms.Textarea(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
                'rows':'3',
                'maxlength':'600'
            }
        )
    )
    etapa =  forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_FORMATO')),
        label='Etapa',
        #required = False,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'selectize-select sin-borde',
                'placeholder' : 'Etapa',
            }
        )
    )
    estatus =  forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_FORMATO')),
        label='Estatus',
        #required = False,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'selectize-select sin-borde',
                'placeholder' : 'Estatus',
            }
        )
    )
    archivo = forms.FileField(
        required = False,
        widget= forms.ClearableFileInput(
            attrs={
                'multiple': False,
                #'class': 'form-control input-rec float-label',
                #'placeholder' : ' ',
            }
        )
    )
    # usuario =  forms.ModelChoiceField(
    #     queryset= User.objects.filter(areas_id = 4, groups__name__contains='Dictaminador'),
    #     label='Abogado',
    #     #required = False,
    #     initial=0,
    #     widget=forms.Select(
    #         attrs={
    #             'class': 'selectize-select sin-borde',
    #             'placeholder' : 'Abogado',
    #         }
    #     )
    # )

    class Meta: 
        model = Resolutor_detalle
        fields = ['resolutor','etapa','estatus','comentarios','usuario','archivo']

class Form_ResolutorArchivo(forms.ModelForm):
    archivo = forms.FileField(
        required = False,
        widget= forms.ClearableFileInput(
            attrs={
                'multiple': False,
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )

    class Meta: 
        model = Resolutor_detalle
        fields = ['archivo']

class Form_Requisito(forms.ModelForm):
    nombre = forms.CharField(      
        label = 'Nombre',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec float-label',
                'placeholder' : ' ',
            }
        )
    )
    obligatorio = forms.BooleanField(
        label='Obligatorio',
        required = False,
        widget = forms.CheckboxInput(
            attrs={
                'placeholder': ''
            }
        ),
    )
    activo = forms.BooleanField(
        label='Activo',
        required = False,
        widget = forms.CheckboxInput(
            attrs={
                'placeholder': ''
            }
        ),
    )
    tramite = forms.ModelChoiceField(
        queryset= Catalogo.objects.filter(Q(agrupador='SELECT_RESPONSABLE')),
        label='Responsable',
        required = True,
        initial=0,
        widget=forms.Select(
            attrs={
                'class': 'selectize-select sin-borde',
                'placeholder' : 'RESPONSABLE',
            }
        )
    )
    # formato_default = forms.BooleanField(
    #     label='¿Tiene formato?',
    #     required = False,
    #     widget = forms.CheckboxInput(
    #         attrs={
    #             'placeholder': '',
    #             'onChange': 'verArchivo()',

    #         }
    #     ),
    # )
    # archivo = forms.FileField(
    #     required = False,
    #     widget= forms.ClearableFileInput(
    #         attrs={
    #             'multiple': False,
    #             'class': 'form-control input-rec float-label',
    #             'placeholder' : ' ',
    #         }
    #     )
    # )
    
    # usuario =  forms.ModelChoiceField(
    #     queryset= User.objects.filter(areas_id = 4, groups__name__contains='Dictaminador'),
    #     label='Abogado',
    #     #required = False,
    #     initial=0,
    #     widget=forms.Select(
    #         attrs={
    #             'class': 'selectize-select sin-borde',
    #             'placeholder' : 'Abogado',
    #         }
    #     )
    # )

    class Meta: 
        model = Requisitos
        fields = ['nombre','obligatorio','activo'] #,'formato_default','archivo'