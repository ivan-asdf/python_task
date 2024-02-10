import time

from celery import shared_task
from django.db import Error
from app.models import Contact, Domain, Collector, CollectorJob
from .constants import COLLECTOR_JOB_STATUSES, ERRORS

# import app.models as models
# from django.db import models

import whois


@shared_task
def test():
    domain = Domain.objects.first()
    for i in range(1, 11):
        time.sleep(1)
        print(i)
    contact = Contact.objects.create(
        domain=domain,
        contact_type="email",
        contact="dasdas@gmail.com",
        # source=Collector.objects.first(),
        source="scraper",
    )
    contact.save()
    print("CONTACT SAVED")


def add_email_contact(email, job):
    Contact.objects.create(
        user=job.collector.user,
        domain=job.domain,
        collector=job.collector,
        collector_job=job,
        contact_type="email",
        contact=email,
    )


@shared_task
def run_whois_job(collector_job_id):
    collector_job = CollectorJob.objects.get(pk=collector_job_id)
    status = collector_job.status
    if status == COLLECTOR_JOB_STATUSES.CREATED:
        collector_job.status = COLLECTOR_JOB_STATUSES.RUNNING
        collector_job.save()
    elif status == COLLECTOR_JOB_STATUSES.RUNNING:
        pass
    else:
        raise Error(ERRORS.RUNNING_ALREADY_COMPLETE_COLLECTOR_JOB)

    try:
        whois_info = whois.whois(collector_job.domain.name)
    except whois.parser.PywhoisError as e:
        print(f"python-whois error: {e}")
        collector_job.status = COLLECTOR_JOB_STATUSES.INVALID
        collector_job.save()
    else:
        if "emails" in whois_info:
            if isinstance(whois_info["emails"], list):
                for email in whois_info["emails"]:
                    add_email_contact(email, collector_job)
            else:
                email = whois_info["emails"]
                add_email_contact(email, collector_job)

        collector_job.status = COLLECTOR_JOB_STATUSES.COMPLETED
        collector_job.save()

    print("WHOIS JOB RAN", collector_job, whois_info, type(whois_info))
