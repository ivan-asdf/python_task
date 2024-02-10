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

    class Meta:
        db_table = "app_collector_job"

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
        return f"domain: {self.domain.name}, collector: {self.collector.name}, status: {self.status}"


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    collector = models.ForeignKey(Collector, on_delete=models.CASCADE)
    collector_job = models.ForeignKey(
        CollectorJob, on_delete=models.SET_NULL, null=True
    )
    contact_type = models.CharField(max_length=50)
    contact = models.CharField(max_length=254)
