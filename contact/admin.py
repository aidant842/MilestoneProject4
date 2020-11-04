from django.contrib import admin
from .models import Contact


class contactAdmin(admin.ModelAdmin):
    model = Contact
    readonly_fields = (
        'name',
        'email',
        'subject',
        'enquiry',
        'date_sent',
    )

    list_display = (
        'subject',
        'email',
        'date_sent'
    )


admin.site.register(Contact, contactAdmin)
