from django.test import TestCase, Client
from django.shortcuts import get_object_or_404

from .models import Category, Product
from .forms import ProductForm
from profiles.models import User


class testViews(TestCase):

    def setUp(self):

        self.client = Client()

        self.category1 = Category.objects.create(
            name='nature',
            friendly_name='Nature',
        )

        self.category2 = Category.objects.create(
            name='scenery',
            friendly_name='Scenery',
        )

        self.product1 = Product.objects.create(
            category=self.category1,
            name='newproduct',
            description='this product',
            price=9999,
            sku='1234',
        )

        self.product2 = Product.objects.create(
            category=self.category2,
            name='newproduct',
            description='this product',
            price=9999,
            sku='1234',
        )

        self.products = Product.objects.filter(
                             category__name=self.category1.name)

        self.testUser = User.objects.create_user(
            username='test',
            password='test1234',
            email='test@test.com',
        )

        self.adminUser = User.objects.create_superuser(
            username='admin',
            password='admin1234',
            email='admin@admin.com',
        )

    def test_all_products_view(self):
        response = self.client.get('/products/')
        self.assertTemplateUsed(response, 'products/products.html')
        self.assertEqual(response.status_code, 200)

    def test_filtered_products(self):
        response = self.client.get(f'/products/?category={self.category1}')
        self.assertEqual(len(self.products), 1)
        self.assertEqual(response.status_code, 200)

    def test_get_product_detail_view(self):
        response = self.client.get(f'/products/{self.product1.id}/')
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertEqual(response.status_code, 200)

    def test_add_product_view_redirects_if_not_logged_in(self):
        response = self.client.get('/products/add/')
        self.assertEqual(response.status_code, 302)

    def test_add_product_view_redirects_if_logged_in_but_not_superuser(self):
        self.client.force_login(self.testUser)
        response = self.client.get('/products/add/')
        self.assertEqual(response.status_code, 302)

    def test_get_add_product_view_if_superuser(self):
        self.client.force_login(self.adminUser)
        response = self.client.get('/products/add/')
        self.assertEqual(response.status_code, 200)

    def test_adding_new_products(self):
        self.client.force_login(self.adminUser)
        products = Product.objects.all()
        print(len(products))

        add_product_form = ProductForm({
            'category': self.category1.pk,
            'name': 'addnewproduct',
            'description': 'addnewproduct description',
            'price': 9999,
            'sku': 123456,
        })

        self.client.post('/products/add/')
        self.assertTrue(add_product_form.is_valid())

        add_product_form.save()
        updated_products = Product.objects.all()
        print(len(updated_products))

        self.assertEqual(len(updated_products), 3)
