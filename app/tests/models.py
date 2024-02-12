from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth.models import User
from app.models import Domain, Collector, CollectorJob, Contact


class DomainModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")

    def test_domain_creation(self):
        domain = Domain.objects.create(user=self.user, name="example.com")
        self.assertEqual(domain.name, "example.com")
        self.assertEqual(domain.user, self.user)

    def test_invalid_domain(self):
        with self.assertRaises(ValidationError):
            Domain.objects.create(user=self.user, name="invalid")


class CollectorModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")

    def test_collector_creation(self):
        collector = Collector.objects.create(
            user=self.user, name=Collector.WHOIS
        )
        self.assertEqual(collector.name, Collector.WHOIS)
        self.assertEqual(collector.user, self.user)


class CollectorJobModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.domain = Domain.objects.create(user=self.user, name="example.com")
        self.collector = Collector.objects.create(
            user=self.user, name=Collector.WHOIS
        )

    def test_collector_job_creation(self):
        collector_job = CollectorJob.objects.create(
            domain=self.domain,
            collector=self.collector,
            status=CollectorJob.CREATED,
        )
        self.assertEqual(collector_job.domain, self.domain)
        self.assertEqual(collector_job.collector, self.collector)
        self.assertEqual(collector_job.status, CollectorJob.CREATED)

    def test_disabled_collector_job_creation(self):
        self.collector.status = Collector.DISABLED
        self.collector.save()
        with self.assertRaises(ValidationError):
            CollectorJob.objects.create(
                domain=self.domain,
                collector=self.collector,
                status=CollectorJob.CREATED,
            )


class ContactModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.domain = Domain.objects.create(user=self.user, name="example.com")
        self.collector = Collector.objects.create(
            user=self.user, name=Collector.WHOIS
        )
        self.collector_job = CollectorJob.objects.create(
            domain=self.domain,
            collector=self.collector,
            status=CollectorJob.CREATED,
        )

    def test_contact_creation(self):
        contact = Contact.objects.create(
            user=self.user,
            domain=self.domain,
            collector=self.collector,
            collector_job=self.collector_job,
            contact_type=Contact.EMAIL,
            contact="test@example.com",
        )
        self.assertEqual(contact.domain, self.domain)
        self.assertEqual(contact.collector, self.collector)
        self.assertEqual(contact.collector_job, self.collector_job)
        self.assertEqual(contact.contact_type, Contact.EMAIL)
        self.assertEqual(contact.contact, "test@example.com")
