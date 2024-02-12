from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from app import views


class UrlsTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='test', password='test')

    def test_index_url_no_login(self):
        url = reverse("index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/")

    def test_index_url_with_login(self):
        url = reverse("index")
        self.client.login(username="test", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # self.assertRedirects(response, "/add-site/")

    def test_add_site_url_no_login(self):
        url = reverse("add_site")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/add-site/")

    def test_add_site_url_with_login(self):
        url = reverse("add_site")
        self.client.login(username="test", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_all_contacts_url_no_login(self):
        url = reverse("all_contacts")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/all-contacts/")

    def test_all_contacts_url_with_login(self):
        url = reverse("all_contacts")
        self.client.login(username="test", password="test")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_collectors_url_no_login(self):
        url = reverse("collectors")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/collectors/")

    def test_collectors_url_with_login(self):
        url = reverse("collectors")
        self.client.login(username="test", password="test")
        response = self.client.get(url)
        self.client.login(username="test", password="test")
        self.assertEqual(response.status_code, 200)
