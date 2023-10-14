from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinLengthValidator
from django.contrib.auth.validators import UnicodeUsernameValidator

def LogoUploadTo(instance, filename):
    return f"uploads/{instance.username}/logo/{filename}"

def CustomUploadTo(instance, filename):
    return f"uploads/{instance.account.username}/{filename}"


class Account(AbstractUser):

    username_validator = UnicodeUsernameValidator()
    
    id = models.BigAutoField(_("ID"), auto_created=True, primary_key=True, serialize=False)
    
    username = models.CharField(_("Usuario"),max_length=64,unique=True, validators=[username_validator],
                help_text=_("Caracters Max-64, Únicamente letras, dígitos y @/./+/-/_"),
                error_messages={"unique": _("¡Usuario Actualmente en Uso!"),},)

    is_staff = models.BooleanField(_("¿Staff?"), default=False)
    is_active = models.BooleanField(_("¿Activo?"), default=True)

    is_inspector = models.BooleanField(_("¿Inspector?"),default=False)

    first_name = models.CharField(_("Nombre"), max_length=150, null=False, blank=False)
    last_name = models.CharField(_("Apellido"), max_length=150, null=False, blank=False)
    email = models.EmailField(_("Email"), unique=True, null=False, blank=False)
    
    date_joined = models.DateField(_("Inscrito"), default=timezone.now)

    company_id = models.CharField(_("ID"), max_length=128, unique=True, null=False, blank=False)
    company = models.CharField(_("Organizacion"), max_length=128, unique=True, null=False, blank=False)
    nit = models.CharField(_("NIT"), max_length=128, unique=True, null=False, blank=False)
    phone = models.CharField(_("Telefono"), max_length=64)
    
    logo = models.ImageField(_("Logo"), upload_to=LogoUploadTo, max_length=32, null=True, blank=True)

    country = models.CharField(_("Pais"), max_length=64)
    state = models.CharField(_("Departamento"), max_length=64)
    city = models.CharField(_("Municipio"), max_length=64)
    address = models.CharField(_("Direccion"), max_length=128)

    billing_code = models.CharField(_("Codigo"), max_length=150, unique=True, null=False, blank=False)
    payment = models.IntegerField(_("Trimestralidad"), default=200000, null=False, blank=False, help_text="$Trimestralidad")

    payment_date = models.DateField(_("Actual"), default=timezone.now, help_text="Fecha de Facturacion")
    due_date = models.DateField(_("Suspencion"), default=timezone.now, help_text="Fecha de Vencimiento ")
    last_due_date = models.DateField(_("Anterior"), default=timezone.now, help_text="Ultima Facturacion")

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


class AccountBilling(models.Model):

    lst_sts = (('current','Actual'),('paid','Abonada'),('overdue','Vencida'))

    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    company_id = models.CharField(_("ID Empresarial"), max_length=128, null=False, blank=False)
    company = models.CharField(_("Organizacion"), max_length=128)

    invoice = models.CharField(_("Facturacion"), max_length=150, blank=True)
    method = models.CharField(_("Metodo"), max_length=150, blank=True)
    debt = models.IntegerField(_("Saldo"), default=0, null=True, blank=True, help_text="$Saldos")
    payment = models.IntegerField(_("WEB"), default=0, null=True, blank=True, help_text="$WEB")
    balance = models.IntegerField(_("Abonos"), default=0, null=True, blank=True, help_text="$Abono")
    discount = models.IntegerField(_("Descuentos"), default=0, null=True, blank=True, help_text="$Descuentos")
    others = models.IntegerField(_("Otros"), default=0, null=True, blank=True, help_text="$Otros")
    payment_total = models.IntegerField(_("Total"), default=0, null=True, blank=True, help_text="$Total")

    voucher = models.CharField(_("Voucher"), max_length=150, blank=True)

    date_invoice = models.DateField(_("Fecha"), default=timezone.now, help_text="Fecha de Emision")
    date_payment = models.DateField(_("Facturado"), default=timezone.now, help_text="Fecha de Facturacion")
    date_dolimit = models.DateField(_("Finaliza"), default=timezone.now, help_text="Fecha de Vencimiento")

    date_succes = models.DateField(_("Abonada"), default=timezone.now, help_text="Fecha Abonada")


    state = models.CharField(choices=lst_sts, max_length=64, verbose_name="", default='current', null=False, blank=False, 
        help_text="Abonada: Factura Cancelada/ Facturar: Factura Vencida/Pendiente")

    def save(self, *args, **kwargs):
        try:
            last_id = AccountBilling.objects.latest('id').id
        except ObjectDoesNotExist:
            last_id = 0

        companyID = self.account.company_id
        if not self.invoice:
            self.invoice = "X0-"+ companyID + "-" + str(100 + last_id)
        super(AccountBilling, self).save(*args, **kwargs)

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
    date = models.DateField(auto_now_add=True)
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
    
    date = models.DateField(auto_now_add=True)
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
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    first_name = models.CharField(_("Nombre"), max_length=64, blank=True)
    last_name = models.CharField(_("Apellido"), max_length=64, blank=True)
    email = models.EmailField(_("Email"), unique=True, null=False, blank=False)
    date = models.DateField(_("Fecha"), default=timezone.now)
    type = models.CharField(max_length=100, choices=TYPES)
    messages = models.TextField(_("Mensaje"),max_length=256,blank=True,null=True)
    is_view = models.BooleanField(_("¿Visto?"),default=False)

    class Meta:
        verbose_name = _("Mensaje")
        verbose_name_plural = _("Mensajes")

    def __str__(self):
        return "%s" % (self.id)




class Files(models.Model):
    code = models.CharField(_("Codigo"), max_length=8, validators=[MinLengthValidator(8)])
    filename = models.CharField(_("Nombre"), max_length=128, null=False, blank=False)

    normative = models.CharField(_("Normativa"), max_length=64, null=False, blank=False)
    entity = models.CharField(_("Entidad"), max_length=64, null=False, blank=False)

    update = models.DateField(_("Actualizado"), default=timezone.now)
    validity = models.IntegerField(_("Vigencia (Dias)"), default=365, null=False, blank=False, help_text="$Valides del Documento")

    is_active = models.BooleanField(_("¿Activo?"), default=True)

    def __str__(self):
        return f"{self.code}"

    class Meta:
        verbose_name = _("Archivo")
        verbose_name_plural = _("Archivos")



class AccountBillingAddons(models.Model):
    billing = models.ForeignKey(AccountBilling, on_delete=models.CASCADE)
    code = models.ForeignKey(Files, on_delete=models.CASCADE)
    price = models.IntegerField(_("Valor"), default=0, null=True, blank=True, help_text="$Valor del Documento")
    filename = models.CharField(_("Nombre"), max_length=128, null=False, blank=False)
    file = models.FileField(_("Archivos"),upload_to=CustomUploadTo, max_length=256, null=False, blank=False)
    date_request = models.DateField(_("Solicitado"), default=timezone.now)
    file_validity = models.DateField(_("Vencimiento"), default=timezone.now)

    def __str__(self):
        return f"{self.code}"
    
    class Meta:
        verbose_name = _("Documento")
        verbose_name_plural = _("Documentos")



class AccountFiles(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    code = models.ForeignKey(Files, on_delete=models.CASCADE)
    filename = models.CharField(_("Nombre"), max_length=128, null=False, blank=False)
    files = models.FileField(_("Archivos"),upload_to=CustomUploadTo, max_length=256, null=False, blank=False)
    
    file_date = models.DateField(_("Inscrito"), default=timezone.now)
    file_validity = models.DateField(_("Vencimiento"), default=timezone.now)

    file_state = models.BooleanField(_("¿Disponible?"), default=True)

    def save(self, *args, **kwargs):
        try:
            last_id = AccountFiles.objects.latest('id').id
        except ObjectDoesNotExist:
            last_id = 0

        companyID = self.account.company_id
        if not self.code:
            self.code = "F0-"+ companyID + "-" + str(100 + last_id)
        super(AccountFiles, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.filename}"
    
    class Meta:
        verbose_name = _("Archivo")
        verbose_name_plural = _("Documentacion")



class RequestFiles(models.Model):

    lst_sts = (('waiting','Pendiente'),('send','Activado'),('bill','Facturado'))

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    code = models.ForeignKey(Files, on_delete=models.CASCADE)
    filename = models.CharField(_("Nombre"), max_length=128, null=False, blank=False)

    file = models.FileField(_("Archivo"),upload_to=CustomUploadTo, max_length=256, null=False, blank=False)
    price = models.BigIntegerField(_("$Costo"), default=0, null=True, blank=True, help_text="$Valor del Documento")
    date_request = models.DateField(_("Solicitado"), default=timezone.now)
    file_validity = models.DateField(_("Vencimiento"), default=timezone.now)

    do = models.CharField(choices=lst_sts, max_length=64, default='waiting', verbose_name="", null=False, blank=False, 
        help_text="Activar: Enviar Archivo sin Facturar/ Facturar: Facturar Documento sin Enviar")

    def __str__(self):
        return f"Solicitud: {self.code}"

    class Meta:
        verbose_name = _("Solicitud")
        verbose_name_plural = _("Solicitudes")



class Settings(models.Model):

    default = models.CharField(max_length=64, blank=True, null=True, default="AiecoConfig", verbose_name="")
    nit = models.CharField(_("NIT"), max_length=64, blank=True, null=True)

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
        return f"{self.default}"

    class Meta:
        verbose_name = _("Configuracion")
        verbose_name_plural = _("Configuraciones")


class PaymentMethods(models.Model):
    settings = models.ForeignKey(Settings, on_delete=models.CASCADE)
    bank = models.CharField(_("Entidad"), max_length=64, blank=True, null=True)
    bank_account = models.CharField(_("#Cuenta"), max_length=64, blank=True, null=True)

    owner = models.CharField(_("Titular"), max_length=64, blank=True, null=True)
    owner_id = models.CharField(_("Cedula"), max_length=64, blank=True, null=True)
    is_active = models.BooleanField(_("¿Activo?"), default=True)

    def __str__(self):
        return f"Configuracion: {self.id}"

    class Meta:
        verbose_name = _("Metodo de Pago")
        verbose_name_plural = _("Metodos de Pago")