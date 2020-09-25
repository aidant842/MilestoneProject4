import uuid

from django.db import models
from django.db.models import Sum

from products.models import Product, Material, Size, Colour


class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=30, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.IntegerField(null=False, default=0)
    order_total = models.IntegerField(null=False, default=0)
    grand_total = models.IntegerField(null=False, default=0)
    original_bag = models.TextField(null=False, blank=False, default='')
    stripe_pid = models.CharField(max_length=254, null=False, blank=False, default='')

    def _generate_order_number(self):
        """ Generate a random, unique order number using UUID """

        return uuid.uuid4().hex.upper()

    def update_total(self):
        """ Update grand total each time an item is added to the order,
        accounting for delivery costs """

        self.order_total = (self.lineitems.aggregate(Sum('lineitem_total'))
                            ['lineitem_total__sum'] or 0)
        self.delivery_cost = int(self.order_total * 0.1)
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """ Override the origonal save method to set the order number
        if it hasn't already been set """

        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = (models.ForeignKey(Order, null=False, blank=False,
             on_delete=models.CASCADE, related_name='lineitems'))
    product = (models.ForeignKey(Product, null=False,
               blank=False, on_delete=models.CASCADE))
    product_size = models.ForeignKey(Size, null=False, blank=False,
                                     on_delete=models.CASCADE, default='')
    product_material = models.ForeignKey(Material, null=False, blank=False,
                                         on_delete=models.CASCADE, default='')
    product_colour = models.ForeignKey(Colour, null=False, blank=False,
                                       on_delete=models.CASCADE, default='')
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = (models.IntegerField(null=False,
                      blank=False, editable=False))

    def save(self, *args, **kwargs):

        """ Override the origonal save method to set the lineitem total
        and update the order total """

        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{ self.order.order_number }'
