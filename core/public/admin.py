from ckeditor.widgets import CKEditorWidget

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.admin import UserAdmin
from django.conf.locale.es import formats as es_formats


import public.models as model

class AuthAdminSite(admin.AdminSite):
    index_title = 'Panel Administrativo'
    verbose_name = "AIECO"

    def get_app_list(self, request, app_label=None):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site. NewMetod for ordering Models
        """
        ordering = {
            "Usuarios": 1,
            "Solicitudes": 2,
            "Facturacion": 3,
            "Anuncios": 4,
            "Mensajes": 5,
            "Multimedia": 6,
            "Links": 7,
            "Archivos": 8,
            "Configuraciones": 9,
            }
        
        app_dict = self._build_app_dict(request, app_label)

        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

        for app in app_list:
            app['models'].sort(key=lambda x: ordering[x['name']])

        return app_list

class PaymentMethodsInline(admin.StackedInline):
    
    model = model.PaymentMethods
    extra = 0
    dFile = {"fields": (
            ("owner","owner_id"),
            ("bank","bank_account","is_active"),
        )}

    fieldsets = (
        (" ", dFile),)

class FilesInline(admin.StackedInline):
    
    model = model.AccountFiles
    extra = 0
    dFile = {"fields": (
            ("code","filename"),
            ("files","file_state"),
            ("file_date","file_validity")
        )}

    fieldsets = (
        (" ", dFile),)


    readonly_fields = ('filename','file_date','code','files',)

    def has_add_permission(self, request, obj=None):
        return False

class NotificationInline(admin.StackedInline):
    
    model = model.AccountNotification
    fk_name = "account"
    extra = 0
    dNotification = {"fields": (
            "sender",
            ("subject","read","archived"),
            "message"
        )}

    fieldsets = (
        ("", dNotification),)
    
    readonly_fields = ('sender','read','archived')


class AccountBillingAddonsInline(admin.StackedInline):
    
    model = model.AccountBillingAddons
    fk_name = "billing"
    extra = 0
    dNotification = {"fields": (
            ("code","file"),
            ("date_request","file_validity","price"),
        )}

    fieldsets = (
        ("", dNotification),)
    
    readonly_fields = ["file","code","date_request","file_validity","price",]

    def has_add_permission(self, request, obj=None):
        return False

class AccountAdmin(UserAdmin):
    
    list_display = (
        "company_id",
        "username",
        "company",
        "email",
        "city",
        "date_joined",
        "is_active"
        )

    dInformation = {"fields": (
            ("username","company_id"),
            ("password"),
            ("company","nit","is_active","is_inspector"),
            
        )}

    dDetails = {"fields": (
            ("first_name","last_name"),
            ("email","phone"),
            ("country","state"),
            ("city","address"),
            ("logo"),
        )}

    dBilling = {"fields": (
            ("billing_code","payment"),
            ("last_due_date","payment_date","due_date"),
        )}

    add_fieldsets = (
        (None,
            {
                "classes": ("wide",),
                "fields": (
                    ("username","payment"),
                    ("password1", "password2"),
                    "email",
                    ("company","nit"),
                ),
            },
        ),
    )

    fieldsets = (
        ("Informacion", dInformation),
        ("Detalles", dDetails),
        ("Facturacion", dBilling),
        )

    list_filter = ['city','is_active','is_inspector']
    search_fields = ['username','company','company_id','email']

    readonly_fields = ('username','billing_code','company','nit','company_id',"last_due_date","payment_date","due_date",)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.username:
            return self.readonly_fields
        return ['billing_code','company_id',"last_due_date","payment_date","due_date",]

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        self.inlines = [FilesInline, NotificationInline]
        if obj and obj.is_superuser or obj is None:
            fieldsets = [fieldsets[0]]
            self.inlines = []
        
        if obj and obj.is_inspector and not obj.is_superuser:
            fieldsets = [fieldsets[0]]
            self.inlines = [NotificationInline]
        
        return fieldsets


class AccountBillingAdmin(admin.ModelAdmin):
    
    list_display = (
        "invoice",
        "company",
        "method",
        "debt",
        "payment_total",
        "date_invoice",
        "state"
        )

    dBillingInfo = {"fields": (
            ("account","company_id","company"),
            ("method","voucher"),
            ("date_invoice","date_payment","date_dolimit","state"),
            ("payment","balance","discount",),
            ("others","debt","payment_total"),
            
        )}

    dDate = {"fields": (
            "date_succes",
        )}

    fieldsets = (
            ("Facturacion", dBillingInfo),
            ("Fecha", dDate),
        )

    list_filter = ['state','method','date_invoice']
    search_fields = ['invoice','company']


    es_formats.DATETIME_FORMAT = "d M Y"
    radio_fields = {'state': admin.HORIZONTAL}
 
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        self.inlines = [AccountBillingAddonsInline]
        if obj and obj.state != "paid":
            fieldsets = [fieldsets[0]]
            if obj.state == "overdue":
                self.inlines = []
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.state != "current":
            return [field.name for field in self.model._meta.fields]
        return ["account","company_id","company","date_invoice","date_dolimit","date_payment","date_succes","payment","others","debt","payment_total"]
    
    def has_add_permission(self, request, obj=None):
        return False


class MediaFilesAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "description",
        "is_active",
        )

    fConfig = {"fields": (
        ("title","is_active"),
        "file",
        "description"
        )}

    fieldsets = (
        ("Multimedia", fConfig),
        )

    list_filter = ['is_active']
    search_fields = ['title']

class InformationAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "url",
        "file",
        "is_active",
        )

    fConfig = {"fields": (
        ("title","is_active"),
        ("url","file"),
        "description"
        )}

    fieldsets = (
        ("Configuracion", fConfig),
        )

    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},}

    list_filter = ['is_active']
    search_fields = ['title']

class AnnouncementsAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "date",
        "description",
        "is_active",
        )

    fConfig = {"fields": (
        ("title","is_active"),
        "description",
        )}

    fieldsets = (
        ("Anuncios", fConfig),
        )

    list_filter = ['is_active']
    search_fields = ['title']

class MessagesAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "account",
        "first_name",
        "last_name",
        "email",
        "date",
        "type",
        "is_view",
        )

    fConfig = {"fields": (
        ("account","email","is_view"),
        ("first_name","last_name"),
        ("date","type"),
        "messages"
        )}

    fieldsets = (
        ("Configuracion", fConfig),
        )

    readonly_fields = ('account','email','first_name','last_name','type','date','messages',)

    def has_add_permission(self, request, obj=None):
        return False

    list_filter = ['is_view','type','date']
    search_fields = ['account','email','first_name','last_name']

class FilesAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "filename",
        "normative",
        "entity",
        "update",
        "validity",
        "is_active",
        )

    fFile = {"fields": (
        ("code","filename"),
        ("entity","normative"),
        ("update","validity","is_active"),
        

        )}

    fieldsets = (
        ("Informacion", fFile),
        )

    es_formats.DATETIME_FORMAT = "d M Y"

    list_filter = ['is_active','entity']
    search_fields = ['code','filename','normative']

class RequestFilesAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "code",
        "account",
        "filename",
        "price",
        "do",
        )

    fFile = {"fields": (
        ("account","code","filename"),
        ("file","price"),
        ("file_validity","do"),
        )}

    fieldsets = (
        ("Informacion", fFile),
        )

    es_formats.DATETIME_FORMAT = "d M Y"
    radio_fields = {'do': admin.HORIZONTAL}

    list_filter = ['do']
    search_fields = ['account','code','filename']

    def has_add_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.do in ["send", "bill"]:
            return [field.name for field in self.model._meta.fields]
        return ['account','code','filename']

class SettingsAdmin(admin.ModelAdmin):

    inlines = [PaymentMethodsInline]
    
    list_display = (
        "default",
        "nit",
        "email",
        "phone",
        "address",
        )

    fConfig = {"fields": (
        "nit",
        ("idx","phone"),
        ("email","address"),
        )}

    fTimes = {"fields": (
        ("opening","closing"),
        )}

    fSocial = {"fields": (
        "twitter",
        "facebook",
        "linkedin",
        )}

    fText = {"fields": (
        "file",
        "about_us",
        "mission",
        "vision",
        "values",
        )}

    fieldsets = (
        ("Configuracion", fConfig),
        ("Horarios", fTimes),
        ("Social", fSocial),
        ("Informacion", fText),
        )

    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},}

    def has_add_permission(self, request):
         return False if model.Settings.objects.exists() else True

    readonly_fields=['default',]


admin_site = AuthAdminSite()
admin.site = admin_site

admin_site.site_header = "AIECO"



admin.site.register(model.Account, AccountAdmin)
admin.site.register(model.AccountBilling, AccountBillingAdmin)
admin.site.register(model.Messages, MessagesAdmin)
admin.site.register(model.Announcements, AnnouncementsAdmin)
admin.site.register(model.MediaFiles, MediaFilesAdmin)
admin.site.register(model.Information, InformationAdmin)
admin.site.register(model.Files, FilesAdmin)
admin.site.register(model.RequestFiles, RequestFilesAdmin)
admin.site.register(model.Settings, SettingsAdmin)
