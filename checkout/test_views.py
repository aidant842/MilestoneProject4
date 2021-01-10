from django.test import TestCase
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.messages import get_messages

from .forms import OrderForm
from .models import Order, OrderLineItem

from profiles.models import User, UserProfile
from products.models import Category, Product, Material, Size, Colour
from profiles.forms import UserProfileForm


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

        self.testUser = User.objects.create_user(
            username='test',
            password='test1234',
            email='test@test.com',
        )

    def test_get_checkout_view(self):
        session = self.client.session
        session['bag'] = self.bag_with_item
        session.save()
        response = self.client.get('/checkout/')
        self.assertEqual(response.status_code, 200)

    def test_checkout_post_view(self):
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

    def test_checkout_get_view(self):
        # Check redirect if no bag in session
        response = self.client.get('/checkout/')
        self.assertEqual(response.status_code, 302)

        # Check load with bag in session
        session = self.client.session
        session['bag'] = self.bag_with_item
        session.save()

        response = self.client.get('/checkout/')
        self.assertEqual(response.status_code, 200)

    def test_checkout_view_profile_does_not_exist(self):
        session = self.client.session
        session['bag'] = self.bag_with_item
        session.save()
        self.client.force_login(self.testUser)
        profile = UserProfile.objects.filter(user=self.testUser)
        # Delete autogenerated profile
        profile.delete()
        response = self.client.get('/checkout/')
        order_form = response.context['order_form']
        self.assertEqual(len(order_form.initial), 0)

    def test_checkout_view_autofill_if_logged_in_with_info_saved(self):
        # Check if user is authenticated, autofil form
        session = self.client.session
        session['bag'] = self.bag_with_item
        session.save()
        self.client.force_login(self.testUser)
        response = self.client.get('/checkout/')
        user_profile = get_object_or_404(UserProfile, user=self.testUser)
        user_profile_form = UserProfileForm({
            'default_phone_number': '0851234567',
            'default_street_address11': 'here',
            'default_street_address2': 'here',
            'default_town_or_city': 'herecity',
            'default_county': 'herecounty',
            'default_postcode': 'herepostcode',
            'default_country': 'US'
        },
            instance=user_profile
        )

        self.assertTrue(user_profile_form.is_valid())
        user_profile_form.save()
        order_form = response.context['order_form']
        self.assertGreater(len(order_form.initial), 1)

    def test_checkout_stripe_key_not_found(self):
        session = self.client.session
        session['bag'] = self.bag_with_item
        session.save()
        settings.STRIPE_PUBLIC_KEY = ''
        response = self.client.get('/checkout/')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'No stripe public key found')

    def test_get_checkout_success_view(self):
        session = self.client.session
        session['save_info'] = True
        session.save()
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
        order = order_form.save()
        response = self.client.get('/checkout/checkout_success'
                                   f'/{order.order_number}/')
        self.assertEqual(response.status_code, 200)

        # Test saving order to user profile if logged in

        self.client.force_login(self.testUser)
        response = self.client.get('/checkout/checkout_success/'
                                   f'{order.order_number}/')
        user_profile = get_object_or_404(UserProfile, user=self.testUser)
        user_profile_form = UserProfileForm({
            'default_phone_number': '0851234567',
            'default_street_address11': 'here',
            'default_street_address2': 'here',
            'default_town_or_city': 'herecity',
            'default_county': 'herecounty',
            'default_postcode': 'herepostcode',
            'default_country': 'US'
        },
            instance=user_profile
        )

        self.assertTrue(user_profile_form.is_valid())
        user_profile_form.save()
        order = Order.objects.get(user_profile=user_profile)
        user_profile = UserProfile.objects.get(user=self.testUser)
        self.assertEqual(order.user_profile.default_phone_number,
                         user_profile.default_phone_number)

        # Test if save info is True
        order.phone_number = '0861234567'
        order.save()
        response = self.client.get('/checkout/checkout_success/'
                                   f'{order.order_number}/')
        self.assertEqual(order.user_profile.default_phone_number,
                         user_profile.default_phone_number)

        # Check to see if bag is deleted
        self.assertFalse(self.client.session.get('bag'))

    def test_order_admin_view(self):
        # Check to see if redirects if not superuser
        self.client.force_login(self.testUser)
        response = self.client.get('/checkout/order_admin/')
        self.assertEqual(response.status_code, 302)
        self.client.logout()

        # Test successful request if admin
        self.client.force_login(self.adminUser)
        response = self.client.get('/checkout/order_admin/')
        self.assertEqual(response.status_code, 200)

    def test_order_detail_view(self):
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
        order = order_form.save()

        # Test redirect if not admin
        self.client.force_login(self.testUser)
        response = self.client.get(f'/checkout/order_admin/{order.id}/')
        self.assertEqual(response.status_code, 302)
        self.client.logout()

        # Test successful request if admin
        self.client.force_login(self.adminUser)
        response = self.client.get(f'/checkout/order_admin/{order.id}/')
        self.assertEqual(response.status_code, 200)

    def test_order_detail_form_error(self):
        self.client.force_login(self.adminUser)
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
        order = order_form.save()

        form_data = {
            'lineitems-TOTAL_FORMS': 1,
            'lineitems-INITIAL_FORMS': 0,
            'lineitems-MIN_NUM_FORMS': 0,
            'lineitems-MAX_NUM_FORMS': 1000,
        }

        response = self.client.post(f'/checkout/order_admin/{order.id}/',
                                    form_data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Update failed, please ensure the'
                         ' product form is valid.')
