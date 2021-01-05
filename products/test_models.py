from django.test import TestCase

from .models import Category, Product, Colour, Size, Material


class TestModels(TestCase):

    def setUp(self):

        self.category1 = Category.objects.create(
            name='nature',
            friendly_name='Nature',
        )

        self.product1 = Product.objects.create(
            category=self.category1,
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

    def test_category_str_method_returns_name(self):
        category = self.category1
        self.assertEqual(str(category), 'nature')

    def test_category_get_friendly_name(self):
        category = self.category1
        self.assertEqual(category.get_friendly_name(), 'Nature')

    def test_product_str_method_returns_name(self):
        product = self.product1
        self.assertEqual(str(product), 'newproduct')

    def test_material_str_method_returns_value(self):
        material = self.material
        self.assertEqual(str(material), 'material')

    def test_size_str_method_returns_value(self):
        size = self.size
        self.assertEqual(str(size), 'XS')

    def test_colour_str_method_returns_name(self):
        colour = self.colour
        self.assertEqual(str(colour), 'Black & White')
