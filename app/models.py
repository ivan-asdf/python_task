from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .constants import COLLECTOR_NAMES

# Create your models here.


class Contact(models.Model):
    site = models.CharField(max_length=100)
    contact_type = models.CharField(max_length=50)
    contact = models.CharField(max_length=100)
    source = models.CharField(max_length=100)

    # def __str__(self):
    #     return self.contact


class Collector(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=True)

    def clean(self):
        super().clean()
        if self.name not in COLLECTOR_NAMES.ALL:
            raise ValidationError("Invalid collector name")

    # def __str__(self):
    #     return self.name


@receiver(post_save, sender=User)
def create_collector(sender, instance, created, **kwargs):
    if created:
        for name in COLLECTOR_NAMES.ALL:
            Collector.objects.create(user=instance, name=name)
