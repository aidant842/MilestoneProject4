from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import UserProfile
from .forms import UserProfileForm, UserEditForm


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.testUser = User.objects.create_user(
            username='test',
            email='test@test.com',
            password='thisisatest',
        )

        self.testUserProfile = get_object_or_404(UserProfile,
                                                 user=self.testUser)

    def test_get_profile_view(self):
        self.client.login(username=self.testUser.username,
                          password=self.testUser.password)
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('profiles/profile.html')

    def test_get_profile_update_view(self):
        self.client.login(username='test', password='thisisatest')
        self.client.get('/profile/update_profile/')
        self.assertTemplateUsed('profiles/update_profile.html')

    def test_update_profile_works(self):
        self.client.login(username=self.testUser.username,
                          password=self.testUser.password)

        user = get_object_or_404(User, username=self.testUser.username)
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

        user_edit_form = UserEditForm({
            'email': 'testemail@testemail.com'
            },
            instance=user
        )

        self.client.post('/profile/update_profile/')

        self.assertTrue(user_profile_form.is_valid())
        self.assertTrue(user_edit_form.is_valid())

        user_edit_form.save()
        user_profile_form.save()

        updated_user_profile = get_object_or_404(UserProfile, user=user)
        updated_user = get_object_or_404(User, username=user.username)

        self.assertEqual(updated_user_profile.default_county, 'herecounty')
        self.assertEqual(updated_user.email, 'testemail@testemail.com')
