from rest_framework.serializers import SerializerMethodField, Serializer
from rest_framework import serializers
from .models import REC, REC_Notificados, Circulo_Credito

class RECSerializer(Serializer):

    rfc = SerializerMethodField()
    nombre = SerializerMethodField()
    direccion = SerializerMethodField()

    def get_rfc(self, obj):
        return obj[0]

    def get_nombre(self, obj):
        return obj[1]

    def get_direccion(self, obj):
        return obj[2]


class REC_Serializer(serializers.ModelSerializer):
    class Meta:
        model = REC_Notificados
        fields = (
            'rfc',
            'nombre',
            'direccion',
        )

class Circulo_Credito_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Circulo_Credito
        fields = (
            'rfc',
            'tipo_persona',
            'razon_social',
            'nombre',
            'apellido_paterno',
            'apellido_materno',
            'curp',
            'fecha_nacimiento',
            'sexo',
            'nacionalidad',
            'numero_ext',
            'numero_int',
            'colonia',
            'ciudad',
            'municipio',
            'estado',
            'cp',
            'telefono',
            'adeudo',
            'fecha_alta',
            'id',
            'fecha_ultimo_pago',
            'interlocutor',
            'objeto_contrato',
            'clave',
            'sub_clave',
            'importe_baja',
            'periodo',
            'ejercicio',
            'area',
            'descripcion',
            'usuario',
            'numero_cuenta',
        )
