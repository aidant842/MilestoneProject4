from django.test import TestCase
import datetime

from .models import Inbox


class TestModels(TestCase):

    def setUp(self):

        self.contact = Inbox.objects.create(
            name='testUser',
            email='test@test.com',
            subject='subject',
            enquiry='enquiry',
            date_sent=datetime.datetime.now(),
            mark_as_read=False,
        )

    def test_str_method_returns_name(self):
        contact = self.contact
        self.assertEqual(str(contact), 'testUser')
