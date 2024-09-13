import datetime

from django import forms
from django.db.models.expressions import F
from .models import Compartidos, Oficios, Permisos, Recibidos
from applications.home.models import Codigos_Maestros
from applications.users.models import User



class OficiosForm(forms.ModelForm): 

    folio = forms.CharField(
        max_length=50,
        label = 'Folio:',
        required = False,
        #initial = get_folio(),
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'style': 'display:none'
            }
        )
    )

    nombre = forms.CharField(
        max_length=400,
        label = 'A quien va dirigido:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    puesto = forms.CharField(
        max_length=400,
        label = 'Puesto:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    asunto = forms.CharField(
        max_length=400,
        label = 'Asunto:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    dependencia = forms.CharField(
        max_length=400,
        label = 'Dependencia:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    fecha = forms.DateField(
        label = 'Fecha Captura:',
        required = True,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'value': 'Select Date',
                'readonly': 'readonly',
                #'format': 'dd/mm/yyyy' 
                #'data-target': '#datapicker'
            } 
        )
    )

    enviado = forms.ModelChoiceField(
        queryset = User.objects.filter(is_superuser=False),
        label = 'Enviado por:', 
        initial = 0,
        widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    firma = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXFIRM'),
       #queryset = Codigos_Maestros.objects.None(),
       label = 'Firma:', 
       initial = 1,
       widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    pdf = forms.FileField(required = False)

    class Meta: 
        model = Oficios 
        fields = ["folio", "nombre", "puesto", "dependencia", "asunto", "fecha", "enviado", "firma", "pdf"]


class CerrarForm(forms.Form):
    
    estatus = forms.CharField(
       label = 'Estatus:', 
       required = False,
       widget = forms.TextInput(
            attrs={
                'class': 'form-control ',
                'readonly': 'readonly'
            }
        )
    )

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


class CerrarRecibidoForm(forms.Form):
    
    estatus = forms.CharField(
       label = 'Estatus:', 
       required = False,
       widget = forms.TextInput(
            attrs={
                'class': 'form-control ',
                'readonly': 'readonly'
            }
        )
    )

    comentarios = forms.CharField(
        max_length=600,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'class': 'form-control input-rec',
                'rows': '5',
                'placeholder': 'Comentarios'
            }
        )
    )

    pdf_respuesta = forms.FileField(
        required = False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder' : 'pdf'
            }
        )
    )



class PermisosForm(forms.ModelForm):

    usuario = forms.CharField(
       label = 'Usuario:', 
       initial = 0,
       widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    permisos = forms.ModelMultipleChoiceField(
       queryset = None,
       label = 'Asignar:', 
       required = False,
       #initial = 0,
       widget = forms.CheckboxSelectMultiple(
            attrs={
                'class': ''
            }
        )
    )   

    class Meta: 
        model = Permisos 
        fields = ["usuario", "permisos"]

    def __init__(self, username, *args, **kwargs):
        self.username = username

        super(PermisosForm, self).__init__(*args, **kwargs)
        self.fields['permisos'] = forms.ModelMultipleChoiceField(
            queryset=User.objects.filter(is_superuser=False).exclude(username=username), 
            widget = forms.CheckboxSelectMultiple(),
            required = False
        )


class CompartidosForm(forms.ModelForm):

    usuario = forms.CharField(
       label = 'Usuario:', 
       initial = 0,
       widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    compartidos = forms.ModelMultipleChoiceField(
       queryset = None,
       label = 'Asignar:', 
       required = False,
       #initial = 0,
       widget = forms.CheckboxSelectMultiple(
            attrs={
                'class': ''
            }
        )
    )   

    class Meta: 
        model = Compartidos  
        fields = ["usuario", "compartidos"]

    def __init__(self, username, unidad, *args, **kwargs):
        self.username = username
        self.unidad = unidad

        super(CompartidosForm, self).__init__(*args, **kwargs)
        self.fields['compartidos'] = forms.ModelMultipleChoiceField(
            #queryset=User.objects.filter(is_superuser=False).exclude(username=username), 
            queryset = User.objects.filter(
                is_superuser=False, 
                is_active=True,
                unidad = unidad
            ),
            widget = forms.CheckboxSelectMultiple(),
            required = False
        )



class RecibidosForm(forms.ModelForm): 

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

    remitente = forms.CharField(
        max_length=400,
        label = 'Remitente:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    puesto = forms.CharField(
        max_length=400,
        label = 'Puesto:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    asunto = forms.CharField(
        max_length=400,
        label = 'Asunto:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    dependencia = forms.CharField(
        max_length=400,
        label = 'Dependencia:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    comentarios = forms.CharField(
        max_length=400,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3
            }
        )
    )
    
    fecha = forms.DateField(
        label = 'Fecha:',
        required = False,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy' 
            } 
        )
    )

    fecha_respuesta = forms.DateField(
        label = 'Fecha Respuesta:',
        required = False,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy' 
            } 
        )
    )
    
    area = forms.CharField(
        label = 'Area:', 
        required=False,
    )
    
    para = forms.CharField(
        label = 'Para:', 
        required=False,
    )

    firma = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXFIRM'),
       label = 'Firma:', 
       initial = 1,
       widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    pdf = forms.FileField(
        required = False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    class Meta: 
        model = Recibidos 
        fields = ["folio", "remitente", "para", "puesto", "dependencia", "asunto", "fecha", "fecha_respuesta", "area", "comentarios", "firma", "pdf"]


class RecibidosForm(forms.ModelForm): 

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

    remitente = forms.CharField(
        max_length=400,
        label = 'Remitente:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    puesto = forms.CharField(
        max_length=400,
        label = 'Puesto:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    asunto = forms.CharField(
        max_length=400,
        label = 'Asunto:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    dependencia = forms.CharField(
        max_length=400,
        label = 'Dependencia:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    comentarios = forms.CharField(
        max_length=400,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3
            }
        )
    )
    
    fecha = forms.DateField(
        label = 'Fecha:',
        required = False,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy' 
            } 
        )
    )

    fecha_respuesta = forms.DateField(
        label = 'Fecha Respuesta:',
        required = False,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy' 
            } 
        )
    )
    
    area = forms.CharField(
        label = 'Area:', 
        required=False,
    )
    
    para = forms.CharField(
        label = 'Para:', 
        required=False,
    )

    firma = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXFIRM'),
       label = 'Firma:', 
       initial = 1,
       widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )

    pdf = forms.FileField(
        required = False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

    class Meta: 
        model = Recibidos 
        fields = ["folio", "remitente", "para", 
                  "puesto", "dependencia", "asunto", 
                  "fecha", "fecha_respuesta", "area", 
                  "comentarios", "firma", "pdf"]



class NuevoOficioForm(forms.Form): 

    folio = forms.CharField(
        max_length=50,
        label = 'Folio:',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'style': 'display:none'
            }
        )
    )

    nombre = forms.CharField(
        max_length=400,
        label = 'A quien va dirigido:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': 'A quien va dirigido:'
            }
        )
    )

    enviado = forms.ModelChoiceField(
        queryset = User.objects.filter(is_superuser=False),
        label = 'Enviado por:', 
        initial = 0,
        widget = forms.Select(
            attrs={
                'class': 'form-control'
            }
        )
    )
    
    puesto = forms.CharField(
        max_length=400,
        label = 'Puesto:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': 'Puesto'
            }
        )
    )
    
    asunto = forms.CharField(
        max_length=400,
        label = 'Asunto:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': 'Asunto'
            }
        )
    )

    dependencia = forms.CharField(
        max_length=400,
        label = 'Dependencia:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': 'Dependencia'
            }
        )
    )

    comentarios = forms.CharField(
        max_length=400,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3
            }
        )
    )
    
    fecha = forms.DateField(
        label = 'Fecha:',
        required = False,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default input-rec',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy' 
            } 
        )
    )

    copia_a = forms.CharField(
        label = 'Copiar a:', 
        required=False,
        widget = forms.Select(
            attrs = {
                'class': 'form-control input-rec'
            }
        )
    )

    firma = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXFIRM'),
       label = 'Firma:', 
       initial = 1,
       widget = forms.Select(
            attrs={
                 'class': 'form-control input-rec',
                'placeholder': 'Firma'
            }
        )
    )

    pdf = forms.FileField(
        required = False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )


class TurnarForm(forms.Form):

    fecha_vencimiento = forms.DateField(
        label = 'Fecha Vencimiento:',
        required = False,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default input-rec',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy',
                'placeholder' : 'Fecha vencimiento' 
            } 
        )
    )
    
    comentarios = forms.CharField(
        max_length=400,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                'class': 'form-control input-rec',
                'rows': 3,
                'placeholder' : 'Comentarios'
            }
        )
    )
    
    turnar_a = forms.CharField(
        label = 'Turnar a:', 
        required=False,
    )

    copiar_a = forms.CharField(
        label = 'Copiar a:', 
        required=False,
    )

class RecibirOficioForm(forms.Form): 

    folio = forms.CharField(
        max_length=50,
        label = 'Folio:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': 'Folio'
            }
        )
    )

    remitente = forms.CharField(
        max_length=400,
        label = 'Remitente:',
        required = True,
        widget = forms.TextInput(
            attrs={
                 'class': 'form-control input-rec ',
                'placeholder': 'Remitente'
            }
        )
    )
    
    puesto = forms.CharField(
        max_length=400,
        label = 'Puesto:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': 'Puesto'
            }
        )
    )
    
    asunto = forms.CharField(
        max_length=400,
        label = 'Asunto:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': 'Asunto'
            }
        )
    )

    cc_externas = forms.CharField(
        max_length=400,
        label = 'Copias Externas:',
        required = False,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': 'Copias'
            }
        )
    )

    dependencia = forms.CharField(
        max_length=400,
        label = 'Dependencia:',
        required = True,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': 'Dependencia'
            }
        )
    )

    comentarios = forms.CharField(
        max_length=400,
        label = 'Comentarios:',
        required = False,
        widget = forms.Textarea(
            attrs={
                 'class': 'form-control input-rec',
                'rows': 3,
                'placeholder': 'Comentarios'
            }
        )
    )
    
    fecha = forms.DateField(
        label = 'Fecha:',
        required = False,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default input-rec',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy' 
            } 
        )
    )

    fecha_respuesta = forms.DateField(
        label = 'Fecha Respuesta:',
        required = False,
        initial=datetime.date.today,
        widget = forms.DateInput(
            attrs={
                'class': 'form-control date-picker-default',
                'readonly': 'readonly',
                'format': 'dd/mm/yyyy' 
            } 
        )
    )
    
    area = forms.CharField(
        label = 'Area:', 
        required=False,
    )
    
    para = forms.CharField(
        label = 'Para:', 
        required=False,
        widget = forms.Select(
            attrs={
                'class': 'form-control input-rec',
                'placeholder': 'Para'
            }
        )
    )

    copiar_a = forms.CharField(
        label = 'Copiar a:', 
        required=False,
        widget = forms.Select(
            attrs = {
                'class': 'form-control input-rec ',
                'placeholder': 'copiar'
                
            }
        )
    )

    turnar_a = forms.CharField(
        label = 'Turnar a:', 
        required=False,
    )

    firma = forms.ModelChoiceField(
       queryset = Codigos_Maestros.objects.filter(codigo='XXFIRM'),
       label = 'Firma:', 
       initial = 1,
       widget = forms.Select(
            attrs={
                'class': 'form-control input-rec'
            }
        )
    )

    pdf = forms.FileField(
        required = False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control input-rec'
            }
        )
    )
