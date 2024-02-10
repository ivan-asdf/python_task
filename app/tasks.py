from celery import shared_task
from django.db import Error
from .models import Contact, CollectorJob
from .constants import ERRORS

import whois


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
    if status == CollectorJob.CREATED:
        collector_job.status = CollectorJob.RUNNING
        collector_job.save()
    elif status == CollectorJob.RUNNING:
        pass
    else:
        raise Error(ERRORS.RUNNING_ALREADY_COMPLETE_COLLECTOR_JOB)

    try:
        whois_info = whois.whois(collector_job.domain.name)
    except whois.parser.PywhoisError as e:
        print(f"python-whois error: {e}")
        collector_job.status = CollectorJob.INVALID
        collector_job.save()
    else:
        if "emails" in whois_info:
            if isinstance(whois_info["emails"], list):
                for email in whois_info["emails"]:
                    add_email_contact(email, collector_job)
            else:
                email = whois_info["emails"]
                add_email_contact(email, collector_job)

        collector_job.status = CollectorJob.COMPLETED
        collector_job.save()

    print("WHOIS JOB RAN", collector_job, whois_info, type(whois_info))
