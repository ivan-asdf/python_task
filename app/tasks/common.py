from app.models import CollectorJob, Contact


def change_job_status(job):
    status = job.status
    if status == CollectorJob.CREATED:
        job.status = CollectorJob.RUNNING
        job.save()
    elif status == CollectorJob.RUNNING:
        pass
    else:
        raise Error(ERRORS.RUNNING_ALREADY_COMPLETE_COLLECTOR_JOB)


def create_contact(job, contact_type, contact):
    Contact.objects.create(
        user=job.collector.user,
        domain=job.domain,
        collector=job.collector,
        collector_job=job,
        contact_type=contact_type,
        contact=contact,
    )
