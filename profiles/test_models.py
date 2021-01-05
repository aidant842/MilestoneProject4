from django.test import TestCase
from django.shortcuts import get_object_or_404
from .models import UserProfile, User


class TestModels(TestCase):

    def test_str_returns_username(self):
        user = User.objects.create_user(
            username='testUser',
            password='pass1234',
            email='test@test.com'
        )

        user_profile = get_object_or_404(UserProfile, user=user)

        self.assertEqual(str(user_profile), 'testUser')
