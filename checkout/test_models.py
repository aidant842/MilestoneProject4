from django.test import TestCase

from .forms import OrderForm
from .models import OrderLineItem

from profiles.models import User
from products.models import Product, Category, Material, Colour, Size


class TestModels(TestCase):

    def setUp(self):
        self.adminUser = User.objects.create_superuser(
            username='admin',
            password='admin1234',
            email='admin@admin.com',
        )

        self.category = Category.objects.create(
            name='nature',
            friendly_name='Nature',
        )

        self.item = Product.objects.create(
            category=self.category,
            name='newproduct',
            description='this product',
            price=9999,
            sku='1234',
        )

        self.product = Product.objects.create(
            category=self.category,
            name='newproduct',
            description='this product',
            price=9999,
            sku='1234',
        )

        self.material = Material.objects.create(
            value='material'
        )

        self.size = Size.objects.create(
            value='XS'
        )

        self.colour = Colour.objects.create(
            name='Black & White'
        )

        self.quantity = 1

        self.order_form = OrderForm({
            'full_name': 'Adam Lee',
            'email': 'test@test.com',
            'phone_number': '0851234567',
            'country': 'US',
            'postcode': 'here',
            'town_or_city': 'herecity',
            'street_address1': 'herestreet',
            'street_address2': 'herestreet2',
            'county': 'herecounty'
        })
        self.order = self.order_form.save()

        self.order_line_item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            product_size=self.size,
            product_material=self.material,
            product_colour=self.colour,
            quantity=self.quantity
        )
        self.order_line_item.save()

    def test_order_str_method(self):
        order = self.order
        self.assertEqual(str(order), self.order.order_number)

    def test_orderlineitem_str_method(self):
        order_line_item = self.order_line_item
        self.assertEqual(str(order_line_item), self.order.order_number)
