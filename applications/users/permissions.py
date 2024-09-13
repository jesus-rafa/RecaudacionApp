from django import template
from django.contrib.auth.models import Permission

register = template.Library()


@register.simple_tag
def has_perms(user, *permissions):

    try:
        perfil = []
        for group in user.groups.all():
            perfil.append(group.id)

        check = Permission.objects.filter(
            group__in=perfil,
            codename__in=permissions
        )

        access = False
        if check:
            access = True

    except:
        access = False

    return access