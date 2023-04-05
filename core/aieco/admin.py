from django.contrib import admin

from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

import aieco.models as model

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
            "Configuraciones": 2,
            }
        
        app_dict = self._build_app_dict(request, app_label)

        app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

        for app in app_list:
            app['models'].sort(key=lambda x: ordering[x['name']])

        return app_list



class FilesInline(admin.StackedInline):
    
    model = model.AccountFiles
    dFile = {"fields": (
            "filename",
            "files",
            ("file_date","file_validity")
        )}

    fieldsets = (
        (" ", dFile),)

class AccountAdmin(admin.ModelAdmin):
    
    inlines = [FilesInline]
    
    list_display = (
        "id",
        "company",
        "email",
        "city",
        "date_joined",
        "is_active"
        )

    dInformation = {"fields": (
            ("username","is_active","is_staff"),
            ("first_name","last_name"),
            ("email","phone"),
            ("company","nit"),
            ("country","state"),
            ("city","address"),
            "logo"
        )}

    fieldsets = (
        ("INFORMACION", dInformation),)

    list_filter = ["date_joined","is_active"]
    search_fields = ['company']


class SettingsAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "sName",
        "sURL",
        "sTel",
        "sEmail"
        )

    fConfig = {"fields": (
        ("sName","IsActive"),
        "sURL",
        ("sIdx","sTel"),
        "sEmail",
        "sAddress"
        )}


    fSocial = {"fields": (
        "sURL1",
        "sURL2",
        "sURL3",
        )}

    fTimes = {"fields": (
        ("sTime1","sTime2"),
        )}

    fieldsets = (
        ("Configuracion", fConfig),
        ("Social", fSocial),
        ("Horarios Atencion", fTimes)
        )


admin_site = AuthAdminSite()
admin.site = admin_site

admin_site.site_header = "AIECO"



admin.site.register(model.Account, AccountAdmin)
admin.site.register(model.Settings, SettingsAdmin)
