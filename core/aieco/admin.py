from django.contrib import admin

from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from .models import Account, AccountFiles



admin.site.unregister(Group)

class GEAdminSite(admin.AdminSite):
    index_title = 'Panel Administrativo'
    verbose_name = "AIECO"

admin_site = GEAdminSite()
admin.site = admin_site

admin_site.site_header = "AIECO"

class FilesInline(admin.StackedInline):
    
    model = AccountFiles

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
            ("city","address")
        )}

    fieldsets = (
        ("INFROMACION", dInformation),)

    list_filter = ["date_joined","is_active"]
    search_fields = ['company']



admin.site.register(Account, AccountAdmin)

