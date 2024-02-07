from django.db import models

# Create your models here.


class Contact(models.Model):
    site = models.CharField(max_length=100)
    contact_type = models.CharField(max_length=50)
    contact = models.CharField(max_length=100)
    source = models.CharField(max_length=100)

    def __str__(self):
        return self.contact

class Collector(models.Model):
    collection_name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    # You can add more fields as needed for your Collector model

    def __str__(self):
        return self.collection_name
