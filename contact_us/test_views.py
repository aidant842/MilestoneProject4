from django.test import TestCase, Client
from django.contrib.messages import get_messages
from django.shortcuts import get_object_or_404
import datetime

from .models import Inbox
from .forms import MarkAsReadForm

from profiles.models import User, UserProfile


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()

        self.contact = Inbox.objects.create(
            name='testUser',
            email='test@test.com',
            subject='subject',
            enquiry='enquiry',
            date_sent=datetime.datetime.now(),
            mark_as_read=False,
        )

        self.contact.save()

        self.adminUser = User.objects.create_superuser(
            username='admin',
            password='admin1234',
            email='admin@admin.com',
        )

        self.testUser = User.objects.create_user(
            username='test',
            password='test1234',
            email='test@test.com',
        )

        self.mar_form = MarkAsReadForm({
            'mark_as_read': True,
        })

    def test_get_contact_us_view(self):
        response = self.client.get('/contact_us/')
        self.assertEqual(response.status_code, 200)

    def test_contact_page_gets_profile_if_logged_in(self):
        self.client.force_login(self.testUser)
        self.client.get('/contact_us/')
        user = get_object_or_404(UserProfile, user=self.testUser)
        self.assertTrue(user, self.testUser)

    def test_get_inbox_view(self):
        self.client.force_login(self.adminUser)
        response = self.client.get('/contact_us/inbox/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        response = self.client.get('/contact_us/inbox/')
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.testUser)
        response = self.client.get('/contact_us/inbox/')
        self.assertEqual(response.status_code, 302)

    def test_get_message_view(self):
        self.client.force_login(self.adminUser)
        response = self.client.get(f'/contact_us/inbox/{self.contact.id}/')
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        response = self.client.get(f'/contact_us/inbox/{self.contact.id}/')
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.testUser)
        response = self.client.get(f'/contact_us/inbox/{self.contact.id}/')
        self.assertEqual(response.status_code, 302)

    def test_mar_form(self):
        self.client.force_login(self.adminUser)
        mar_form = self.mar_form
        self.client.post(f'/contact_us/inbox/{self.contact.id}/')
        self.assertTrue(mar_form.is_valid())
        mar_form.save()

    def test_delete_message_view(self):
        response = self.client.get(f'/contact_us/delete/{self.contact.id}/')
        self.assertEqual(response.status_code, 302)

    def test_delete_message(self):
        self.client.force_login(self.adminUser)
        message = self.contact
        response = self.client.post(f'/contact_us/delete/{message.id}/')
        message.delete()
        updated_inbox = Inbox.objects.all()
        self.assertEqual(len(updated_inbox), 0)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]),
                         'Message deleted successfully!')
