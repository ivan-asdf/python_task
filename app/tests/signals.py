from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_migrate
from django.test.utils import override_settings
from app.models import Domain, Collector, CollectorJob
from app.signals import (
    create_test_user,
    create_collector,
    create_collector_jobs,
    run_collector_jobs,
)


class SignalsTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        post_save.disconnect(create_test_user, sender=User)
        post_save.disconnect(create_collector, sender=User)
        post_save.disconnect(create_collector_jobs, sender=Domain)
        post_save.disconnect(run_collector_jobs, sender=CollectorJob)

    def setUp(self):
        self.user = User.objects.create(username="test_user")

    @override_settings(DEBUG=True)
    def test_create_test_user_signal(self):
        create_test_user(sender=None)
        self.assertTrue(User.objects.filter(username="asdf").exists())

    def test_create_collector_signal(self):
        create_collector(sender=User, instance=self.user, created=True)
        collectors = Collector.objects.filter(user=self.user)
        self.assertEqual(collectors.count(), len(Collector.NAME_CHOICES))

    def test_create_collector_jobs_signal(self):
        domain = Domain.objects.create(user=self.user, name="example.com")
        create_collector_jobs(sender=Domain, instance=domain, created=True)
        collector_jobs = CollectorJob.objects.filter(domain=domain)
        self.assertEqual(collector_jobs.count(), len(Collector.objects.all()))

    def test_run_collector_jobs_signal(self):
        domain = Domain.objects.create(user=self.user, name="example.com")
        collector = Collector.objects.create(
            user=self.user, name=Collector.WHOIS
        )
        collector_job = CollectorJob.objects.create(
            domain=domain, collector=collector, status=CollectorJob.CREATED
        )
        run_collector_jobs(
            sender=CollectorJob, instance=collector_job, created=True
        )
        # Add assertions as needed for the expected behavior
        # For example, check if a task is queued or executed
