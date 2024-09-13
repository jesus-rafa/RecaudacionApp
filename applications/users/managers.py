from django.db import models
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager, models.Manager):

    def _create_user(self, email, nombres, apellidos, password, is_staff, is_active, is_superuser, **extra_fields):
        user = self.model(
            email = email,
            nombres = nombres,
            apellidos = apellidos,
            is_staff = is_staff,
            is_active = is_active,
            is_superuser = is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, email, nombres, apellidos, password=None, **extra_fields):
        return self._create_user(email, nombres, apellidos, password, True, True, False, **extra_fields)


    def create_superuser(self, email, nombres, apellidos, password=None, **extra_fields):
        return self._create_user(email, nombres, apellidos, password, True, True, True, **extra_fields)