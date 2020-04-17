from django.db import models

class Site(models.Model):
    guid = models.CharField(max_length=40, primary_key=True)
    name = models.CharField(max_length=128)
    url = models.CharField(max_length=1024)
    last_check = models.DateTimeField(auto_now_add=True, null=True)
    last_up = models.DateTimeField(null=True)
    last_down = models.DateTimeField(null=True)
    last_change = models.DateTimeField(null=True)
    uptime_hour = models.FloatField(null=True)
    uptime_day = models.FloatField(null=True)
    uptime_week = models.FloatField(null=True)
    uptime_30 = models.FloatField(null=True)
    uptime_90 = models.FloatField(null=True)

    class Meta:
        ordering = ['name']

class Check(models.Model):
    guid = models.CharField(max_length=40)
    timestamp = models.DateTimeField(auto_now_add=True)
    data = models.CharField(max_length=40,null=True)
    data_unfiltered = models.CharField(max_length=40,null=True)
    tries = models.IntegerField(null=True)
    etag = models.CharField(max_length=64,null=True)

    class Meta:
        ordering = ['-timestamp']
        
class Blob(models.Model):
    guid = models.CharField(max_length=40, primary_key=True)
    data = models.TextField()
