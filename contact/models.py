from django.db import models

# Create your models here.


class Contact(models.Model):
    """ A model for the contact form to send questions to the admin panel """
    name = models.CharField(max_length=254, editable=False, blank=False, null=False)
    email = models.EmailField(max_length=254, editable=False, blank=False, null=False)
    enquiry = models.TextField(max_length=1024, editable=False, blank=False, null=False)

    def __str__(self):
        return self.name
