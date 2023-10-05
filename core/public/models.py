import uuid
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

def LogoUploadTo(instance, filename):
    return f"uploads/{instance.username}/logo/{filename}"

def CustomUploadTo(instance, filename):
    return f"uploads/{instance.account.username}/{filename}"


class Account(AbstractUser):
    
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')

    is_staff = models.BooleanField(_("Staff"),default=False)
    is_active = models.BooleanField(default=True,verbose_name="")

    first_name = models.CharField(_("Nombre"), max_length=150, blank=True)
    last_name = models.CharField(_("Apellido"), max_length=150, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    
    date_joined = models.DateTimeField(_("Inscrito"), default=timezone.now)

    company_id = models.CharField(_("ID Empresarial"), max_length=128, unique=True, null=False, blank=False)
    company = models.CharField(_("Organizacion"), max_length=128)
    nit = models.CharField(_("NIT"), max_length=128)
    phone = models.CharField(_("Telefono"), max_length=64)
    
    logo = models.ImageField(_("Logo"), upload_to=LogoUploadTo, max_length=32, null=True, blank=True)

    country = models.CharField(_("Pais"), max_length=64)
    state = models.CharField(_("Departamento"), max_length=64)
    city = models.CharField(_("Municipio"), max_length=64)
    address = models.CharField(_("Direccion"), max_length=128)

    billing_code = models.CharField(_("Codigo"), max_length=150, blank=True)

    debt = models.IntegerField(_("Saldo"), default=0, null=True, blank=True, help_text="$Saldo")
    payment = models.IntegerField(_("Trimestralidad"), default=200000, null=True, blank=True, help_text="$Trimestralidad")
    balance = models.IntegerField(_("Abonos"), default=0, null=True, blank=True, help_text="$Abonos")
    discount = models.IntegerField(_("Descuentos"), default=0, null=True, blank=True, help_text="$Descuentos")
    others = models.IntegerField(_("Otros"), default=0, null=True, blank=True, help_text="$Otros")
    payment_total = models.IntegerField(_("Total"), default=0, null=True, blank=True, help_text="$Total")

    payment_date = models.DateTimeField(_("Actual"), default=timezone.now, help_text="Fecha de Facturacion")
    due_date = models.DateTimeField(_("Suspencion"), default=timezone.now, help_text="Fecha de Vencimiento ")
    last_due_date = models.DateTimeField(_("Anterior"), default=timezone.now, help_text="Ultima Facturacion")

    def save(self, *args, **kwargs):
        try:
            last_id = Account.objects.latest('id').id
        except ObjectDoesNotExist:
            last_id = 0

        if not self.company_id:
            self.company_id = str(1000 + last_id)

        if not self.billing_code:
            self.billing_code = "A0-" + self.company_id
        super(Account, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}"

    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")


class AccountFiles(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    filename = models.CharField(_("Nombre"), max_length=128, blank=True)
    files = models.FileField(_("Archivos"),upload_to=CustomUploadTo, max_length=256, null=True, blank=True)
    
    file_date = models.DateTimeField(_("Inscrito"), default=timezone.now)
    file_validity = models.DateTimeField(_("Vencimiento"), default=timezone.now)


    def __str__(self):
        return f"{self.filename}"
    
    class Meta:
        verbose_name = _("Archivo")
        verbose_name_plural = _("Documentacion")


class AccountBilling(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    company_id = models.CharField(_("ID Empresarial"), max_length=128, unique=True, null=False, blank=False)
    company = models.CharField(_("Organizacion"), max_length=128)

    invoice = models.CharField(_("Factura"), max_length=150, blank=True)
    method = models.CharField(_("Metodo"), max_length=150, blank=True)
    debt = models.IntegerField(_("Saldo"), default=0, null=True, blank=True, help_text="$Saldo")
    payment = models.IntegerField(_("Total"), default=0, null=True, blank=True, help_text="$Total")

    voucher = models.CharField(_("Voucher"), max_length=150, blank=True)

    date = models.DateTimeField(_("Fecha"), default=timezone.now, help_text="Fecha")

    def __str__(self):
        return f"{self.invoice}"
    
    class Meta:
        verbose_name = _("Factura")
        verbose_name_plural = _("Facturacion")


class AccountNotification(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_notifications')
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sent_notifications')
    subject = models.CharField(_("Asunto"),blank=True, null=True, max_length=64)
    message = models.TextField(_("Mensaje"),blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(_("¿Leido?"),default=False)
    archived = models.BooleanField(_("¿Archivado?"),default=False)

    def save(self, *args, **kwargs):
        self.sender = self.account
        super(AccountNotification, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.id}"
    
    class Meta:
        verbose_name = _("Notifiacion")
        verbose_name_plural = _("Notificaciones")

class MediaFiles(models.Model):

    title = models.CharField(_("Titulo"), max_length=64, blank=False, null=False,
        help_text="Titulo/Encabezado")
    
    file = models.FileField(_("Video"),upload_to="uploads/multimedia/", max_length=256, null=True, blank=True)
    description = models.TextField(_("Descripcion"))
    upload_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(_("¿Activo?"), default=True)

    def __str__(self):
        return f"Multimedia: {self.title}"

    class Meta:
        verbose_name = _("Video")
        verbose_name_plural = _("Multimedia")


class Announcements(models.Model):

    title = models.CharField(_("Titulo"), max_length=64, blank=False, null=False,
        help_text="Titulo/Encabezado")
    
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(_("Texto"))
    is_active = models.BooleanField(_("¿Activo?"), default=True)

    def __str__(self):
        return f"Anuncio: {self.title}"

    class Meta:
        verbose_name = _("Anuncio")
        verbose_name_plural = _("Anuncios")


class Information(models.Model):

    title = models.CharField(_("Titulo"), max_length=64, blank=False, null=False,
        help_text="Titulo/Encabezado")
    
    url = models.CharField(_("URL"), max_length=32, blank=False, null=False, 
        help_text="Local/Ref (SinEspacios-OnlyURL)")
    
    file = models.FileField(_("PDF"),upload_to="uploads/legal/", max_length=256, null=True, blank=True)
    description = models.TextField(_("Texto"))
    is_active = models.BooleanField(_("¿Activo?"), default=True)

    def __str__(self):
        return f"Informacion: {self.title}"

    class Meta:
        verbose_name = _("Link")
        verbose_name_plural = _("Links")


class Messages(models.Model):

    TYPES = (
        ('ticket', 'Solicitud de Servicio'),
        ('billing', 'Facturacion'),
        ('bugs', 'Reporte de Fallo/Error'),
    )
    
    id = models.AutoField(primary_key=True, verbose_name="ID")
    uuid = models.UUIDField(_("Ticket"), primary_key=False, default=uuid.uuid4, editable=False, unique=True, max_length=7)
    first_name = models.CharField(_("Nombre"), max_length=64, blank=True)
    last_name = models.CharField(_("Apellido"), max_length=64, blank=True)
    date = models.DateTimeField(_("Fecha"), default=timezone.now)
    type = models.CharField(max_length=100, choices=TYPES)
    messages = models.TextField(_("Mensaje"),max_length=256,blank=True,null=True)
    is_view = models.BooleanField(_("¿Visto?"),default=False)

    class Meta:
        verbose_name = _("Mensaje")
        verbose_name_plural = _("Mensajes")

    def __str__(self):
        return "%s" % (self.id)


class Settings(models.Model):

    idx = models.SmallIntegerField(_("Indicativo"), blank=True, null=True, default=57)
    phone = models.CharField(_("Telefono"), max_length=64, blank=True, null=True)
    
    email = models.EmailField(_("Correo"), max_length=254, blank=True, null=True)
    
    opening = models.TimeField(_("Inicia"), auto_now=False, auto_now_add=False)
    closing = models.TimeField(_("Finaliza"), auto_now=False, auto_now_add=False)

    address = models.CharField(_("Address"), max_length=64, blank=True, null=True)
    
    twitter = models.URLField(_("Twitter"), max_length=128, blank=True, null=True)
    facebook = models.URLField(_("Facebook"), max_length=128, blank=True, null=True)
    linkedin = models.URLField(_("Linkedin"), max_length=128, blank=True, null=True)

    about_us = models.TextField(_("Texto"),blank=True, null=True,help_text="Texto Informativo ¿Quienes Somos?")
    mission = models.TextField(_("Mision"),blank=True, null=True,help_text="Mision Empresarial")
    vision = models.TextField(_("Vision"),blank=True, null=True,help_text="Vision Empresarial")
    values = models.TextField(_("Valores"),blank=True, null=True,help_text="Valores Empresariales")

    file = models.FileField(_("PDF"),upload_to="uploads/legal/", max_length=256, null=True, blank=True)

    def __str__(self):
        return f"Configuracion: {self.id}"

    class Meta:
        verbose_name = _("Configuracion")
        verbose_name_plural = _("Configuraciones")