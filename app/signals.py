from django.db.models.signals import post_save
from django.dispatch import receiver

from .tasks import run_whois_job
from .models import User, Domain, Collector, CollectorJob

from .constants import COLLECTOR_NAMES, COLLECTOR_STATUSES, COLLECTOR_JOB_STATUSES


@receiver(post_save, sender=User)
def create_collector(sender, instance, created, **kwargs):
    if created:
        for name in COLLECTOR_NAMES.ALL:
            Collector.objects.create(user=instance, name=name)


@receiver(post_save, sender=Domain)
def create_collector_jobs(sender, instance, created, **kwargs):
    for collector in Collector.objects.all():
        if collector.status == COLLECTOR_STATUSES.ACTIVE:
            CollectorJob.objects.create(
                domain=instance,
                collector=collector,
                status=COLLECTOR_JOB_STATUSES.CREATED,
            )


@receiver(post_save, sender=CollectorJob)
def run_collector_jobs(sender, instance, created, **kwargs):
    if created:
        print("RUN_COLLECTOR_JOBS SIGNAL CREATED", instance)
        if instance.collector.name == COLLECTOR_NAMES.WHOIS:
            run_whois_job.delay(instance.id)
