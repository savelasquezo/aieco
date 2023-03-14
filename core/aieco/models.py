from django.db import models

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from django.utils.html import format_html

def LogoUploadTo(instance, filename):
    return f"uploads/{instance.username}/logo/{filename}"

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
    
    logo = models.ImageField(_("Logo"), upload_to=LogoUploadTo, max_length=32)

    country = models.CharField(_("Pais"), max_length=64)
    state = models.CharField(_("Departamento"), max_length=64)
    city = models.CharField(_("Municipio"), max_length=64)
    address = models.CharField(_("Direccion"), max_length=128)

    def __str__(self):
        return f"Empresa: {self.username}"

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


class Settings(models.Model):

    sName = models.CharField(_("Configuracion"), max_length=64, blank=False, null=False, help_text="Organizacion/Empresa")
    sURL = models.URLField(_("URL"), max_length=128, blank=True, null=True)

    sIdx = models.SmallIntegerField(_("Indicativo"), blank=True, null=True, default=57)
    sTel = models.CharField(_("Telefono"), max_length=64, blank=True, null=True)
    
    sEmail = models.EmailField(_("Correo"), max_length=254, blank=True, null=True)
    
    sTime1 = models.TimeField(_("Inicia"), auto_now=False, auto_now_add=False)
    sTime2 = models.TimeField(_("Finaliza"), auto_now=False, auto_now_add=False)

    sAddress = models.CharField(_("Address"), max_length=64, blank=True, null=True)
    
    sURL1 = models.URLField(_("Instagram"), max_length=128, blank=True, null=True)
    sURL2 = models.URLField(_("Facebook"), max_length=128, blank=True, null=True)
    sURL3 = models.URLField(_("Twitter"), max_length=128, blank=True, null=True)

    IsActive = models.BooleanField(_("¿Activo?"), default=True, unique=True)

    def __str__(self):
        return f"Configuracion: {self.sName}"

    class Meta:
        verbose_name = _("Configuracion")
        verbose_name_plural = _("Configuraciones")