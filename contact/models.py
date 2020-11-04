from django.db import models
from datetime import datetime

# Create your models here.


class Contact(models.Model):
    """ A model for the contact form to send questions to the admin panel """
    name = models.CharField(max_length=254, blank=False, null=False)
    email = models.EmailField(max_length=254, blank=False, null=False)
    subject = models.CharField(max_length=64, blank=False,
                               null=False, default="subject")
    enquiry = models.TextField(max_length=1024, blank=False, null=False)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
