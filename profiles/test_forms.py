from django.test import TestCase
from .forms import UserEditForm, UserProfileForm


class TestUserProfileForm(TestCase):

    def test_fields_are_not_required(self):
        form = UserProfileForm({
                                'default_phone_number': '',
                                'default_postcode': '',
                                'default_town_or_city': '',
                                'default_street_address1': '',
                                'default_street_address2': '',
                                'default_county': '',
                                'default_country': '',
                            })

        self.assertTrue(form.is_valid())

        form_list = [
                     'default_phone_number',
                     'default_postcode',
                     'default_town_or_city',
                     'default_street_address1',
                     'default_street_address2',
                     'default_county',
                     'default_country',
        ]
        for item in form_list:
            if item not in form.errors.keys():
                not_required = True
            else:
                not_required = False
            self.assertTrue(not_required)

        self.assertEqual(len(form.errors), 0)

    def test_fields_are_explicit_in_form_metaclass(self):
        form = UserProfileForm()
        form_list = [
                     'default_phone_number',
                     'default_postcode',
                     'default_town_or_city',
                     'default_street_address1',
                     'default_street_address2',
                     'default_county',
                     'default_country',
        ]
        self.assertEqual(form.Meta.fields, form_list)


class TestUserEditForm(TestCase):

    def test_fields_are_not_required(self):
        form = UserProfileForm({
                                'first_name': '',
                                'last_name': '',
                                'email': '',
                            })

        self.assertTrue(form.is_valid())

    def test_fields_are_explicit_in_form_metaclass(self):
        form = UserEditForm()
        form_list = [
            'first_name',
            'last_name',
            'email'
        ]

        self.assertEqual(form.Meta.fields, form_list)
