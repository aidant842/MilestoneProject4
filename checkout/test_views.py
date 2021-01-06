from django.test import TestCase
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.messages import get_messages

from .forms import OrderForm
from .models import Order, OrderLineItem

from profiles.models import User
from products.models import Category, Product, Material, Size, Colour


class TestViews(TestCase):

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

        self.bag = []

        self.bag_with_item = [{
            'item_id': str(self.item.id),
            'item_size': str(self.size),
            'item_material': str(self.material),
            'item_colour': str(self.colour),
            'quantity': int(self.quantity),
            'total': 9999
        }]

        self.bag_with_item_not_exist = [{
            'item_id': str(999),
            'item_size': str(self.size),
            'item_material': str(self.material),
            'item_colour': str(self.colour),
            'quantity': int(self.quantity),
            'total': 9999
        }]

    def test_get_checkout_view(self):
        session = self.client.session
        session['bag'] = self.bag_with_item
        session.save()
        response = self.client.get('/checkout/')
        self.assertEqual(response.status_code, 200)

    def test_checkout_view(self):
        session = self.client.session
        session['bag'] = self.bag_with_item
        session.save()

        post_data = {
            'full_name': 'Adam Lee',
            'email': 'test@test.com',
            'phone_number': '0851234567',
            'country': 'US',
            'postcode': 'here',
            'town_or_city': 'herecity',
            'street_address1': 'herestreet',
            'street_address2': 'herestreet2',
            'county': 'herecounty',
            'client_secret': settings.STRIPE_SECRET_KEY
        }

        order_form = OrderForm({
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
        self.client.post('/checkout/', post_data)
        self.assertTrue(order_form.is_valid())

        order = Order.objects.filter(stripe_pid=post_data['client_secret'])
        get_order = Order.objects.get(stripe_pid=post_data['client_secret'])
        num_orders = order.count()
        self.assertEqual(num_orders, 1)
        order_line_item = get_object_or_404(OrderLineItem, order=get_order)
        self.assertEqual(str(order_line_item.product), self.item.name)

    def test_checkout_view_deletes_order_if_product_doesnt_exist(self):
        session = self.client.session
        session['bag'] = self.bag_with_item_not_exist
        session.save()

        post_data = {
            'full_name': 'Adam Lee',
            'email': 'test@test.com',
            'phone_number': '0851234567',
            'country': 'US',
            'postcode': 'here',
            'town_or_city': 'herecity',
            'street_address1': 'herestreet',
            'street_address2': 'herestreet2',
            'county': 'herecounty',
            'client_secret': settings.STRIPE_SECRET_KEY
        }

        order_form = OrderForm({
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
        self.client.post('/checkout/', post_data)
        self.assertTrue(order_form.is_valid())

        order = Order.objects.filter(stripe_pid=post_data['client_secret'])
        num_orders = order.count()
        self.assertEqual(num_orders, 0)
