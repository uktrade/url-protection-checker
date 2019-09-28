from django.db import models


class Spaces(models.Model):
    space_name = models.CharField(max_length=60)
    space_guid = models.CharField(max_length=60)
    enabled = models.BooleanField(default=True)


class Applications(models.Model):
    app_name = models.CharField(max_length=60)
    primary_app_route = models.URLField(blank=True)
    secondary_app_route = models.URLField(blank=True)
    enabled = models.BooleanField(default=True)
