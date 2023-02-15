from django.db import models

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Account(AbstractUser):

    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")