from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

import validators

from .constants import COLLECTOR_NAMES

# Create your models here.


class Domain(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    domain_name = models.CharField(max_length=253, unique=True)

    def clean(self):
        super().clean()
        if not validators.domain(self.domain_name):
            raise ValidationError("Is not FQDM(Fully Qualified Domain Name)")

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
            raise ValidationError("Invalid collector name")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    # def __str__(self):
    #     return self.name


@receiver(post_save, sender=User)
def create_collector(sender, instance, created, **kwargs):
    if created:
        for name in COLLECTOR_NAMES.ALL:
            Collector.objects.create(user=instance, name=name)
