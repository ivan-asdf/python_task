from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

import validators

# from app.tasks import run_whois_job
# import app.tasks as tasks

from .constants import (
    ERRORS,
)

# Create your models here.


class Domain(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=253, unique=True)

    def clean(self):
        super().clean()
        if not validators.domain(self.name):
            raise ValidationError(ERRORS.NOT_FQDM)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"user: {self.user} name: {self.name}"


class Collector(models.Model):
    WHOIS = "whois"
    SCRAPER = "scrape"
    NAME_CHOICES = [
        (WHOIS, WHOIS),
        (SCRAPER, WHOIS),
    ]

    ENABLED = True
    DISABLED = False
    STATUS_CHOICES = [
        (ENABLED, "ACTIVE"),
        (DISABLED, "INACTIVE"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, choices=NAME_CHOICES)
    status = models.BooleanField(default=ENABLED, choices=STATUS_CHOICES)


class CollectorJob(models.Model):
    CREATED = "created"
    RUNNING = "running"
    INVALID = "invalid"
    COMPLETED = "completed"
    STATUS_CHOICES = [
        (CREATED, CREATED),
        (RUNNING, RUNNING),
        (INVALID, INVALID),
        (COMPLETED, COMPLETED),
    ]

    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        db_table = "app_collector_job"

    def clean(self):
        super().clean()
        if self._state.adding:
            if self.collector.status == Collector.DISABLED:
                raise ValidationError(
                    ERRORS.CREATING_JOB_FOR_DISABLED_COLLECTOR
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"domain: {self.domain.name}, collector: {self.collector.name},"
            f" status: {self.status}"
        )


class Contact(models.Model):
    PHONE = "phone"
    EMAIL = "email"
    CONTACT_TYPE_CHOICES = [
        (PHONE, PHONE),
        (EMAIL, EMAIL),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE)
    collector_job = models.ForeignKey(
        CollectorJob,
        on_delete=models.SET_NULL,
        null=True,
    )
    contact_type = models.CharField(
        max_length=50,
        choices=CONTACT_TYPE_CHOICES,
    )
    contact = models.CharField(max_length=254)
