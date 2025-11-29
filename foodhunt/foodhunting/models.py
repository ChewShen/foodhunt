from django.db import models
import os

# Create your models here.
    
class shopLists(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=300, blank=True, null=True)
    description = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='shopimages/', null=True,blank=True)
    # New recommended fields:
    cuisine = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    area = models.CharField(max_length=50, blank=True, null=True)
    opening_hours = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True)
    # Price range is very useful for your app!
    price = models.CharField(max_length=5, blank=True, null=True) 


    def __str__(self):
        return self.name
    