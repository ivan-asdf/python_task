from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from app.models import Domain, Contact, Collector
from app.views import index, add_site, all_contacts, collectors
from app.constants import ERRORS


class ViewsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="test_user", password="test_password"
        )

    def test_index_view(self):
        request = self.factory.get("/")
        request.user = self.user
        response = index(request)
        self.assertEqual(response.status_code, 302)  # Redirect status code

    def test_add_site_view_get(self):
        request = self.factory.get("/add-site/")
        request.user = self.user
        response = add_site(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("add_site.html")

    def test_add_site_view_post_invalid(self):
        request = self.factory.post(
            "/add-site/", {"domain_name": "invalid-domain"}
        )
        request.user = self.user
        response = add_site(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("add_site.html")
        self.assertContains(response, "ERROR")
        self.assertContains(response, ERRORS.NOT_FQDM)

    def test_add_site_view_post_valid(self):
        request = self.factory.post(
            "/add-site/", {"domain_name": "example.com"}
        )
        request.user = self.user
        response = add_site(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SUCCESS")
        self.assertNotContains(response, "ERROR")
        self.assertNotContains(response, ERRORS.NOT_FQDM)

    def test_all_contacts_view(self):
        request = self.factory.get("/all-contacts/")
        request.user = self.user
        response = all_contacts(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("all_contacts.html")
        self.assertContains(response, "<table>")

    def test_collectors_view_get(self):
        request = self.factory.get("/collectors/")
        request.user = self.user
        response = collectors(request)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("collectors.html")
        self.assertContains(response, "<table>")

    def test_collectors_view_post(self):
        collector = Collector.objects.create(
            user=self.user, name="Test Collector"
        )
        request = self.factory.post(
            "/collectors/", {"collector_id": collector.pk}
        )
        request.user = self.user
        response = collectors(request)
        self.assertEqual(response.status_code, 200)
        updated_collector = Collector.objects.get(pk=collector.pk)
        self.assertNotEqual(collector.status, updated_collector.status)
