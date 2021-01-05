from django.test import TestCase
from .forms import ProductForm


class TestForms(TestCase):

    def test_all_fields_are_displayed(self):
        form = ProductForm()
        self.assertEqual(form.Meta.fields, '__all__')
