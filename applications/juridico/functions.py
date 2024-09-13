from datetime import date
from .models import (Demanda)
from django.db.models import Max
import datetime

def get_username(self):
    username = self.request.user.username

    return username

def get_id_user(self):
    id = self.request.user.id

    return id 

def get_carpeta(juicio):
    print(juicio)
    ultimo_folio = Demanda.objects.filter(juicio=juicio.data['juicio']).values('carpeta').order_by('-id')[:1]
    try:
        separacion = ultimo_folio[0]['carpeta'].split('/')
        consecutivo = int(separacion[0]) + 1
        current_year = date.today().year

        if current_year != int(separacion[1]):
            year = current_year
            consecutivo = 1
        else:
            year = separacion[1]
            
        carpeta = str(consecutivo) + '/' + str(year)
    except:
        carpeta = '1/'+str(date.today().year)        

    return carpeta
