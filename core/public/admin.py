from ckeditor.widgets import CKEditorWidget

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db import models

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
            "Facturacion": 2,
            "Anuncios": 3,
            "Mensajes": 4,
            "Multimedia": 5,
            "Links":6,
            "Configuraciones": 7,
            }
        
        app_dict = self._build_app_dict(request, app_label)

        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

        for app in app_list:
            app['models'].sort(key=lambda x: ordering[x['name']])

        return app_list



class FilesInline(admin.StackedInline):
    
    model = model.AccountFiles
    extra = 0
    dFile = {"fields": (
            "filename",
            "files",
            ("file_date","file_validity")
        )}

    fieldsets = (
        (" ", dFile),)
    
    readonly_fields = ('file_date',)

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

class AccountAdmin(admin.ModelAdmin):
    
    inlines = [FilesInline, NotificationInline]
    
    list_display = (
        "id",
        "company",
        "email",
        "city",
        "date_joined",
        "is_active"
        )

    dInformation = {"fields": (
            ("first_name","last_name"),
            ("email","phone"),
            ("company","nit"),
            ("country","state"),
            ("city","address"),
            ("logo","is_active","is_staff","company_id"),
        )}

    dBillingInfo = {"fields": (
            ("billing_code"),
            ("last_due_date","payment_date","due_date"),
            ("balance","discount","others"),
            ("payment","debt","payment_total"),
        )}


    fieldsets = (
        ("Informacion", dInformation),
        ("Facturacion", dBillingInfo),
        )

    list_filter = ["date_joined","is_active"]
    search_fields = ['company']

    readonly_fields = ('billing_code','company_id',"last_due_date","payment_date","due_date",)


class AccountBillingAdmin(admin.ModelAdmin):
    
    list_display = (
        "company_id",
        "company",
        "invoice",
        "method",
        "debt",
        "payment",
        "date",
        )


    dBillingInfo = {"fields": (
            ("account","invoice"),
            ("company_id","company"),
            ("method","date"),
            ("payment","voucher"),
        )}


    fieldsets = (
        ("Facturacion", dBillingInfo),
        )

    list_filter = ["method"]
    search_fields = ['company']


    readonly_fields = ('account','invoice','company_id','company',)


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

class MessagesAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "first_name",
        "last_name",
        "date",
        "type",
        "is_view",
        )

    fConfig = {"fields": (
        ("first_name","last_name"),
        ("type"),
        "messages"
        )}

    fieldsets = (
        ("Configuracion", fConfig),
        )

    readonly_fields = ('first_name','last_name','type','messages',)


class SettingsAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "email",
        "phone",
        "address",
        )

    fConfig = {"fields": (
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
        ("Horarios Atencion", fTimes),
        ("Social", fSocial),
        ("Informacion", fText),
        )

    formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget()},}

admin_site = AuthAdminSite()
admin.site = admin_site

admin_site.site_header = "AIECO"



admin.site.register(model.Account, AccountAdmin)
admin.site.register(model.AccountBilling, AccountBillingAdmin)
admin.site.register(model.Messages, MessagesAdmin)
admin.site.register(model.Announcements, AnnouncementsAdmin)
admin.site.register(model.MediaFiles, MediaFilesAdmin)
admin.site.register(model.Information, InformationAdmin)
admin.site.register(model.Settings, SettingsAdmin)
