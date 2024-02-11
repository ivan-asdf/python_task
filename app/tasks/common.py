from app.models import CollectorJob


def change_job_status(job):
    status = job.status
    if status == CollectorJob.CREATED:
        job.status = CollectorJob.RUNNING
        job.save()
    elif status == CollectorJob.RUNNING:
        pass
    else:
        raise Error(ERRORS.RUNNING_ALREADY_COMPLETE_COLLECTOR_JOB)
