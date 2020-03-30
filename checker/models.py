from django.db import models


class Orgs(models.Model):
    org_name = models.CharField(max_length=90)
    org_guid = models.CharField(max_length=90)
    check_enabled = models.BooleanField(default=True)


class Spaces(models.Model):
    space_name = models.CharField(max_length=90)
    space_guid = models.CharField(max_length=90)
    check_enabled = models.BooleanField(default=True)
    orgs = models.ForeignKey(Orgs, on_delete=models.CASCADE)


class Applications(models.Model):
    app_name = models.CharField(max_length=90)
    spaces = models.ForeignKey(Spaces, on_delete=models.CASCADE)


class ApplicationsItem(models.Model):
    applications = models.ForeignKey(Applications, on_delete=models.CASCADE)
    app_route = models.URLField(blank=True)
    is_behind_vpn = models.BooleanField(default=False)
    is_behind_sso = models.BooleanField(default=False)
    is_behind_app_auth = models.BooleanField(default=False)
    is_protected = models.BooleanField(default=False)
    reporting_enabled = models.BooleanField(default=True)
    reporting_disabled_reason = models.CharField(max_length=120, blank=True)


class NonPaasSites(models.Model):
    site_name = models.CharField(max_length=90)
    site_url = models.URLField(blank=True)
    is_protected = models.BooleanField(default=False)
    reporting_enabled = models.BooleanField(default=True)
