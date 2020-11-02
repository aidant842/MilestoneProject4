from django.contrib import admin
from .models import Messages


class messagesAdmin(admin.ModelAdmin):
    model = Messages
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


admin.site.register(Messages, messagesAdmin)
