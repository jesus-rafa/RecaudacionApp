# -*- coding: utf-8 -*-
# @Author: shubhambansal
# @Date:   2018-02-04 23:08:11
# @Last Modified by:   shubhambansal
# @Last Modified time: 2018-02-04 23:25:39
from rest_framework import routers
from applications.programacion.viewsets import ModelosViewSet

router = routers.DefaultRouter()

router.register(r'modelos', ModelosViewSet)
