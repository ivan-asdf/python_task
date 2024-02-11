from celery import shared_task
from django.db import Error
from .models import Contact, CollectorJob
from .constants import ERRORS

import whois

def make_sure_list(string_or_list):
    if isinstance(string_or_list, str):
        return [string_or_list]
    elif isinstance(string_or_list, list):
        return string_or_list
    else:
        raise TypeError("Input must be either a string or a list")


def add_contact_from_data(whois_data, whois_data_key, contact_type, job):
    if (contact_type != Contact.EMAIL) and (contact_type != Contact.PHONE):
        raise Error("Invalid contact_type give.")

    if whois_data_key in whois_data:
        contact_data = whois_data[whois_data_key]
        if contact_data is not None:
            contact_data = make_sure_list(contact_data)
            for contact in contact_data:
                Contact.objects.create(
                    user=job.collector.user,
                    domain=job.domain,
                    collector=job.collector,
                    collector_job=job,
                    contact_type=contact_type,
                    contact=contact,
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
        print(whois_info)
        add_contact_from_data(
            whois_info,
            "emails",
            Contact.EMAIL,
            collector_job,
        )
        add_contact_from_data(
            whois_info,
            "phone",
            Contact.PHONE,
            collector_job,
        )

        collector_job.status = CollectorJob.COMPLETED
        collector_job.save()
