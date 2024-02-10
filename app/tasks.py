import time
from celery import shared_task
from .models import Contact, Domain, Collector


@shared_task
def test():
    domain = Domain.objects.first()
    for i in range(1, 11):
        time.sleep(1)
        print(i, "R")
    contact = Contact.objects.create(
        domain=domain,
        contact_type="email",
        contact="dasdas@gmail.com",
        # source=Collector.objects.first(),
        source="scraper",
    )
    contact.save()
    print("CONTACT SAVED")
