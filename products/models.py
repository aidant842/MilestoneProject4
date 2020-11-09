from django.db import models

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    category = models.ForeignKey('Category', null=True,
                                 blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.IntegerField()
    sku = models.CharField(max_length=254, null=True, blank=True)
    image = models.ImageField(default='https://image.flatico\
                              n.com/icons/svg/38/38645.svg')

    def __str__(self):
        return self.name


class Material(models.Model):
    value = models.CharField(max_length=254)

    def __str__(self):
        return self.value


class Size(models.Model):
    value = models.CharField(max_length=254)

    def __str__(self):
        return self.value


class Colour(models.Model):
    name = models.CharField(max_length=254)

    def __str__(self):
        return self.name
