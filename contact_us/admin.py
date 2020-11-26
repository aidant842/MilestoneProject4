from django.contrib import admin
from .models import Inbox


class inboxAdmin(admin.ModelAdmin):
    model = Inbox
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


admin.site.register(Inbox, inboxAdmin)
