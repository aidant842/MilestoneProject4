from django.test import TestCase, Client
from django.contrib.auth.models import User


class TestViews(TestCase):

    def testUser_setup(self):
        testUser = User.objects.create_user(
            username='test',
            email='test@test.com',
            password='thisisatest',
        )
        testUser.save()
        self.tester = Client()

    def test_get_profile_view(self):
        self.client.login(username='test', password='thisisatest')
        self.client.get('/profile/')
        self.assertTemplateUsed('profiles/profile.html')

    def test_get_profile_update_view(self):
        self.client.login(username='test', password='thisisatest')
        self.client.get('/profile/update_profile/')
        self.assertTemplateUsed('profiles/update_profile.html')
