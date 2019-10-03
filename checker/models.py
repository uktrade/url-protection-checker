from django.db import models


class Spaces(models.Model):
    space_name = models.CharField(max_length=60)
    space_guid = models.CharField(max_length=60)
    check_enabled = models.BooleanField(default=True)


class Applications(models.Model):
    app_name = models.CharField(max_length=60)


class ApplicationsItem(models.Model):
    applications = models.ForeignKey(Applications, on_delete=models.CASCADE)
    spaces = models.ForeignKey(Spaces, on_delete=models.CASCADE)
    app_route = models.URLField(blank=True)
    is_behind_vpn = models.BooleanField(default=False)
    is_behind_sso = models.BooleanField(default=False)
    check_enabled = models.BooleanField(default=True)
