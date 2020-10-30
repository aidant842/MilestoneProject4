from django.contrib import admin
from .models import Contact


class contactAdmin(admin.ModelAdmin):
    readonly_fields = [
        'name',
        'email',
        'enquiry',
    ]

    fields = [
        'name',
        'email',
        'enquiry',
    ]


admin.site.register(Contact)
