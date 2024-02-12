from django.db import Error
from django.test import TestCase
from django.contrib.auth.models import User
from app.models import Collector, CollectorJob, Contact, Domain
from app.tasks import make_sure_list, create_contact_from_data, run_whois_job


class SharedSetupTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")

        self.collector = Collector.objects.create(
            user=self.user,
            name=Collector.WHOIS,
            status=Collector.ENABLED,
        )
        self.domain = Domain.objects.create(user=self.user, name="google.at")

        self.collector_job = CollectorJob.objects.create(
            domain=self.domain,
            collector=self.collector,
            status=CollectorJob.CREATED,
        )


class MakeSureListTestCase(TestCase):
    def test_string_input(self):
        input_value = "test"
        result = make_sure_list(input_value)
        self.assertEqual(result, ["test"])

    def test_list_input(self):
        input_value = ["test1", "test2"]
        result = make_sure_list(input_value)
        self.assertEqual(result, input_value)

    def test_other_input(self):
        input_value = 123  # Example of input that is not a string or a list
        with self.assertRaises(TypeError):
            make_sure_list(input_value)


class CreateContactFromDataTestCase(SharedSetupTestCase):
    def test_create_contact_from_data_with_valid_data(self):
        whois_data = {
            "domain_name": "google.at",
            "registrar": "MarkMonitor Inc. ( https://nic.at/registrar/434 )",
            "name": "DNS Admin",
            "org": "Google Inc.",
            "address": "1600 Amphitheatre Parkway",
            "registrant_postal_code": ["94043", "USA-94043"],
            "city": ["Mountain View", "Mountain View, CA"],
            "country": "United States of America (the)",
            "phone": ["+16502530000", "+16506234000"],
            "fax": ["+16502530001", "+16506188571"],
            "updated_date": [
                "2011-04-26 17:57:27",
                "2011-01-11 00:07:31",
                "2005-06-17 21:36:20",
                "2011-01-11 00:08:30",
            ],
            "email": "dns-admin@google.com",
        }
        whois_data_key = "email"
        contact_type = Contact.EMAIL

        create_contact_from_data(
            whois_data, whois_data_key, contact_type, self.collector_job
        )
        self.assertTrue(
            Contact.objects.filter(
                contact="dns-admin@google.com",
                contact_type=Contact.EMAIL,
                user=self.user,
                domain=self.domain,
                collector=self.collector,
                collector_job=self.collector_job,
            ).exists()
        )

        Contact.objects.all().delete()
        # Call with wrong data key
        create_contact_from_data(
            whois_data, "emails", contact_type, self.collector_job
        )
        self.assertFalse(
            Contact.objects.filter(
                contact="dns-admin@google.com",
                contact_type=Contact.EMAIL,
                user=self.user,
                domain=self.domain,
                collector=self.collector,
                collector_job=self.collector_job,
            ).exists()
        )

    def test_create_contact_from_data_with_invalid_contact_type(self):
        whois_data = {"emails": ["test@example.com"], "phone": "123456789"}
        whois_data_key = "emails"
        contact_type = "invalid_contact_type"

        # Assert that an Error is raised when an invalid contact type is given
        with self.assertRaises(Error) as context:
            create_contact_from_data(
                whois_data, whois_data_key, contact_type, self.collector_job
            )
        self.assertIn("invalid", str(context.exception).lower())


class RunWhoisJobTestCase(SharedSetupTestCase):
    def test_run_whois_job(self):
        # Simulate running the Celery task
        run_whois_job(self.collector_job.id)

        # Reload the collector job from the database
        self.collector_job.refresh_from_db()

        # Assert that the status has been updated to COMPLETED
        self.assertEqual(self.collector_job.status, CollectorJob.COMPLETED)

        # Assert that contacts have been created
        emails_count = Contact.objects.filter(
            collector_job=self.collector_job, contact_type=Contact.EMAIL
        ).count()
        phones_count = Contact.objects.filter(
            collector_job=self.collector_job, contact_type=Contact.PHONE
        ).count()

        self.assertNotEqual(emails_count, 0)
        self.assertNotEqual(phones_count, 0)
