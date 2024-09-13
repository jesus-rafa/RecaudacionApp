#from applications.programacion.models import Programa, Detalle


# def insert_detail(sender, instance, **kwargs):
#     print("  ======== Se guardo detalle ========= ")

#     obj = Programa.objects.latest('id')
#     detail = Detalle(
#         programa_id=obj,
#         fecha=instance.fecha,
#         comentarios='Se genero Folio',
#         estatus='VALIDACION',
#     )
#     detail.save()

    # if instance.imagen:
    #     imagen = Image.open(instance.imagen.path)
    #     imagen.save(instance.imagen.path, quality=20, optimize=True)

    # def save(self, *args, **kwargs):
    #     latest = Programa.objects.latest('id')
    #     ID = int(latest.id) + 1
    #     #obj = Programa.objects.latest('id')
    #     obj = Programa.objects.get(pk=ID)

    #     fecha = self.fecha
    #     comentario = 'Se genero folio x'
    #     estatus = 'VALIDACION'
        
    #     detail = Detalle(
    #         programa_id=obj,
    #         fecha=fecha,
    #         comentarios=comentario,
    #         estatus=estatus,
    #     )
    #     detail.save()

    #     super(Programa, self).save(*args, **kwargs)


# def insert_coordenates(sender, instance, **kwargs):
#     print("  ======== Se guardaron coordenadas ============ ")
#     if instance.imagen:
#         base_dir = settings.MEDIA_ROOT
#         path = os.path.join(base_dir, str(instance.imagen))

#         #path = Image.open(instance.imagen.path)
#         lat, long = get_exif_location(get_exif_data(path))

#         if lat == None:
#             lat = '-'
#         if long == None:
#             long = '-'

#         instance.coordenada = str(lat) + ',' + str(long)

#         print('=======: ' + str(instance.coordenada))
        
#         instance.save()

    # else:
    #     instance.coordenada = '-,-'
    #     #instance.coordenada.save()
    #     #instance.datos.save()

    #     print('=======: ' + str(instance.coordenada))

    #     instance.coordenada.save()