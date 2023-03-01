from django.db import models

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.utils.html import format_html

def CustomUploadTo(instance, filename):
    return f"uploads/{instance.account.username}/{filename}"


class Account(AbstractUser):
    
    is_staff = models.BooleanField(_("Staff"),default=False)
    is_active = models.BooleanField(default=True,verbose_name="")

    first_name = models.CharField(_("Nombre"), max_length=150, blank=True)
    last_name = models.CharField(_("Apellido"), max_length=150, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    
    date_joined = models.DateTimeField(_("Inscrito"), default=timezone.now)

    company = models.CharField(_("Organizacion"), max_length=128)
    nit = models.CharField(_("NIT"), max_length=128)
    phone = models.CharField(_("Telefono"), max_length=64)

    country = models.CharField(_("Pais"), max_length=64)
    state = models.CharField(_("Departamento"), max_length=64)
    city = models.CharField(_("Municipio"), max_length=64)
    address = models.CharField(_("Direccion"), max_length=128)

    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")


class AccountFiles(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    filename = models.CharField(_("Nombre"), max_length=128, blank=True)
    files = models.FileField(_("Archivos"),upload_to=CustomUploadTo, max_length=256, null=True, blank=True)

    def __str__(self):
        return f"{self.filename}"
    
    class Meta:
        verbose_name = _("Archivo")
        verbose_name_plural = _("Documentacion")