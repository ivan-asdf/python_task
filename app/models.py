from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User

import validators

# from app.tasks import run_whois_job
# import app.tasks as tasks

from .constants import (
    COLLECTOR_JOB_STATUSES,
    COLLECTOR_NAMES,
    COLLECTOR_STATUSES,
    ERRORS,
)

# Create your models here.


class Domain(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain_name = models.CharField(max_length=253, unique=True)

    def clean(self):
        super().clean()
        if not validators.domain(self.domain_name):
            raise ValidationError(ERRORS.NOT_FQDM)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"user: {self.user} domain_name: {self.domain_name}"


class Contact(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    contact_type = models.CharField(max_length=50)
    contact = models.CharField(max_length=254)
    source = models.CharField(max_length=50)

    # def __str__(self):
    #     return self.contact


class Collector(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    status = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if self.name not in COLLECTOR_NAMES.ALL:
            raise ValidationError(ERRORS.INVALID_COLLECTOR)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # def __str__(self):
    #     return self.name


class CollectorJob(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE)
    status = models.CharField(max_length=20)

    def clean(self):
        super().clean()
        if self._state.adding:
            if self.collector.status == COLLECTOR_STATUSES.INACTIVE:
                raise ValidationError(ERRORS.CREATING_JOB_FOR_DISABLED_COLLECTOR)
        elif self.status not in COLLECTOR_JOB_STATUSES.ALL:
            raise ValidationError(ERRORS.INVALID_STATUS_FOR_COLLECTOR_JOB)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"domain: {self.domain.domain_name}, collector: {self.collector.name}, status: {self.status}"
