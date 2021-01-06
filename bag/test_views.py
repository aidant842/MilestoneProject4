from django.test import TestCase
from django.shortcuts import get_object_or_404
from products.models import Product, Category, Size, Material, Colour


class TestViews(TestCase):

    def setUp(self):

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

        self.new_item = True

        self.bag = []

        self.bag_with_item = [{
            'item_id': str(self.item.id),
            'item_size': str(self.size),
            'item_material': str(self.material),
            'item_colour': str(self.colour),
            'quantity': int(self.quantity),
            'total': 9999
        }]

    def test_get_view_bag_view(self):
        response = self.client.get('/bag/')
        self.assertTrue(response.status_code, 200)

    def test_add_to_bag_view(self):
        post_data = {
            'product': Product.objects.get(pk=self.item.id),
            'quantity': int(self.quantity),
            'bag': self.bag,
            'size': self.size,
            'material': self.material,
            'colour': self.colour,
            'new_item': self.new_item,
            'redirect_url': f'/products/{self.item.id}/'
        }

        response = self.client.post(f'/bag/add/{self.item.id}/', post_data)
        self.assertEqual(response.status_code, 302)
        updated_bag = self.client.session.get('bag')
        self.assertEqual(len(updated_bag), 1)

    def test_add_to_bag_view_updates_item_if_exists(self):
        session = self.client.session
        session['bag'] = self.bag_with_item
        session.save()
        post_data = {
            'product': Product.objects.get(pk=self.item.id),
            'quantity': 3,
            'size': str(self.size),
            'material': str(self.material),
            'colour': str(self.colour),
            'redirect_url': f'/products/{self.item.id}/'
        }
        response = self.client.post(f'/bag/add/{self.item.id}/', post_data)
        self.assertEqual(response.status_code, 302)
        updated_bag = self.client.session.get('bag')
        updated_bag_index = updated_bag[0]
        self.assertEqual(updated_bag_index['quantity'], 4)

    def test_adjust_bag_view(self):
        session = self.client.session
        session['bag'] = self.bag_with_item
        session.save()
        post_data = {
            'bag_item': get_object_or_404(Product, pk=self.item.id),
            'quantity': int(self.quantity + 1),
            'product_size': str(self.size),
            'product_material': str(self.material),
            'product_colour': str(self.colour)
        }

        response = self.client.post(f'/bag/adjust/{self.item.id}/', post_data)
        self.assertEqual(response.status_code, 302)
        updated_bag = self.client.session.get('bag')
        updated_bag_index = updated_bag[0]
        self.assertEqual(updated_bag_index['quantity'], 2)

    def test_adjust_bag_view_removes_item_if_quantity_under_1(self):
        session = self.client.session
        session['bag'] = self.bag_with_item
        session.save()
        post_data = {
            'bag_item': get_object_or_404(Product, pk=self.item.id),
            'quantity': int(self.quantity - 1),
            'product_size': str(self.size),
            'product_material': str(self.material),
            'product_colour': str(self.colour)
        }

        response = self.client.post(f'/bag/adjust/{self.item.id}/', post_data)
        self.assertEqual(response.status_code, 302)
        updated_bag = self.client.session.get('bag')
        self.assertEqual(len(updated_bag), 0)

    def test_remove_from_bag_view(self):
        session = self.client.session
        session['bag'] = self.bag_with_item
        session.save()
        post_data = {
            'size': str(self.size),
            'material': str(self.material),
            'colour': str(self.colour),
        }

        response = self.client.post(f'/bag/remove/{self.item.id}/', post_data)
        self.assertEqual(response.status_code, 200)
        updated_bag = self.client.session.get('bag')
        self.assertEqual(len(updated_bag), 0)

    def test_remove_from_bag_error(self):
        post_data = {}
        response = self.client.post(f'/bag/remove/{self.item.id}/', post_data)
        self.assertEqual(response.status_code, 500)
