import whois

from celery import shared_task
from django.db import Error
from app.models import Contact, CollectorJob

from .common import change_job_status, create_contact


def make_sure_list(string_or_list):
    if isinstance(string_or_list, str):
        return [string_or_list]
    elif isinstance(string_or_list, list):
        return string_or_list
    else:
        raise TypeError("Input must be either a string or a list")


def create_contact_from_data(whois_data, whois_data_key, contact_type, job):
    if (contact_type != Contact.EMAIL) and (contact_type != Contact.PHONE):
        raise Error("Invalid contact_type given.")

    if whois_data_key in whois_data:
        contact_data = whois_data[whois_data_key]
        if contact_data is not None:
            contact_data = make_sure_list(contact_data)
            for contact in contact_data:
                create_contact(job, contact_type, contact)


@shared_task
def run_whois_job(collector_job_id):
    job = CollectorJob.objects.get(pk=collector_job_id)
    change_job_status(job)

    try:
        whois_data = whois.whois(job.domain.name)
    except whois.parser.PywhoisError as e:
        print(f"python-whois error: {e}")
        job.status = CollectorJob.INVALID
        job.save()
    else:
        print(whois_data)
        create_contact_from_data(
            whois_data,
            "emails",
            Contact.EMAIL,
            job,
        )
        create_contact_from_data(
            whois_data,
            "phone",
            Contact.PHONE,
            job,
        )

        job.status = CollectorJob.COMPLETED
        job.save()
