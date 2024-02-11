from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver

from .tasks import run_whois_job
from .models import User, Domain, Collector, CollectorJob


# Create default test user
@receiver(post_migrate)
def create_test_user(sender, **kwargs):
    if not User.objects.filter(username="asdf").exists():
        User.objects.create_user("asdf", password="asdf")


@receiver(post_save, sender=User)
def create_collector(sender, instance, created, **kwargs):
    if created:
        for name in Collector.NAME_CHOICES:
            Collector.objects.create(user=instance, name=name[0])


@receiver(post_save, sender=Domain)
def create_collector_jobs(sender, instance, created, **kwargs):
    for collector in Collector.objects.all():
        if collector.status == Collector.ENABLED:
            CollectorJob.objects.create(
                domain=instance,
                collector=collector,
                status=CollectorJob.CREATED,
            )


@receiver(post_save, sender=CollectorJob)
def run_collector_jobs(sender, instance, created, **kwargs):
    if created:
        print("RUN_COLLECTOR_JOBS SIGNAL CREATED", instance)
        if instance.collector.name == Collector.WHOIS:
            run_whois_job.delay(instance.id)
