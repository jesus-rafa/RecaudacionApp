from rest_framework.serializers import SerializerMethodField, Serializer
from rest_framework import serializers
from .models import Solicitante

class Solicitante_Serialize(serializers.ModelSerializer):
    class Meta:
        model = Solicitante
        fields = (
            'rfc',
            'nombre',
            'apeP',
            'apeM',
            'calle',
            'numero',
            'colonia',
            'ciudad',
            'cp',
            'telefono',
        )