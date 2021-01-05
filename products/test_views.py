from django.test import TestCase, Client
from django.shortcuts import get_object_or_404
from django.contrib.messages import get_messages

from .models import Category, Product
from .forms import ProductForm
from profiles.models import User


class TestViews(TestCase):

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
        self.assertEqual(len(updated_products), 3)

    def test_get_edit_product_view(self):
        # Check successful load if logged in superuser
        self.client.force_login(self.adminUser)
        response = self.client.get(f'/products/edit/{self.product1.id}/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        # Check redirects if not logged in
        response = self.client.get(f'/products/edit/{self.product1.id}/')
        self.assertEqual(response.status_code, 302)

        # Check redirects if logged in but not superuser
        self.client.force_login(self.testUser)
        response = self.client.get(f'/products/edit/{self.product1.id}/')
        self.assertEqual(response.status_code, 302)

    def test_edit_product(self):
        self.client.force_login(self.adminUser)

        product = get_object_or_404(Product, pk=self.product1.id)

        product_form = ProductForm({
            'category': self.category1.pk,
            'name': 'editedproductname',
            'description': 'addnewproduct description',
            'price': 9999,
            'sku': 123456,
        },
            instance=product
        )

        self.assertTrue(product_form.is_valid())
        product_form.save()

        self.client.post(f'/products/edit/{self.product1.id}/')
        updated_product = Product.objects.get(id=self.product1.id)
        self.assertEqual(updated_product.name, 'editedproductname')

    def test_edit_management_view(self):
        self.client.force_login(self.adminUser)
        response = self.client.get('/products/edit_management/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        response = self.client.get('/products/edit_management/')
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.testUser)
        response = self.client.get('/products/edit_management/')
        self.assertEqual(response.status_code, 302)

    def test_delete_management_view(self):
        self.client.force_login(self.adminUser)
        response = self.client.get('/products/delete_management/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        response = self.client.get('/products/delete_management/')
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.testUser)
        response = self.client.get('/products/delete_management/')
        self.assertEqual(response.status_code, 302)

    def test_delete_product(self):
        self.client.force_login(self.adminUser)
        response = self.client.get(f'/products/delete/{self.product1.id}/')
        self.product1.delete()
        updated_products = Product.objects.all()
        self.assertEqual(len(updated_products), 1)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]),
                         f'Success! {self.product1.name} deleted.')
