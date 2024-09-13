# -*- coding: utf-8 -*-
# @Author: rafa lopez
# @Date:   2021-04-19 18:00:00
# @Last Modified by:
# @Last Modified time:
from rest_framework import serializers
from .models import Modelos


class ModelosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modelos
        fields = '__all__'
