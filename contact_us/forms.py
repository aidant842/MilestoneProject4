from django import forms
from .models import Inbox


class MarkAsReadForm(forms.ModelForm):
    class Meta:
        model = Inbox
        fields = ('mark_as_read',)
