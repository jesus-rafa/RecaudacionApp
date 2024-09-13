from PIL import Image


def optimize_image(sender, instance, **kwargs):
    print("  ======== Se optimizo imagen ========= ")
    if instance.imagen:
        imagen = Image.open(instance.imagen.path)
        imagen.save(instance.imagen.path, quality=20, optimize=True)