from django.contrib import admin
from django.contrib import messages

from .models import Spaces, ApplicationsItem, NonPaasSites


def space_toggle_enabled(modeladmin, request, queryset):
    for space_name in queryset:
        if space_name.check_enabled:
            space_name.check_enabled = False
        else:
            space_name.check_enabled = True
        space_name.save()


space_toggle_enabled.short_description = 'Toggle check enabled'


@admin.register(Spaces)
class service_admin(admin.ModelAdmin):
    list_display = ('id', 'space_name', 'space_guid', 'check_enabled')
    actions = [space_toggle_enabled, ]


def toggle_reporting(modeladmin, request, queryset):
    for app_route in queryset:
        if app_route.reporting_enabled:
            app_route.reporting_enabled = False
        else:
            app_route.reporting_enabled = True
        app_route.save()


toggle_reporting.short_description = 'Toggle check enabled'


@admin.register(ApplicationsItem)
class applicationsitem_admin(admin.ModelAdmin):
    list_display = ('id',
                    'org_name',
                    'space_name',
                    'app_name',
                    'app_route',
                    'is_behind_vpn',
                    'is_behind_sso',
                    'is_behind_app_auth',
                    'reporting_enabled',
                    'is_protected',
                    'reporting_disabled_reason')
    actions = [toggle_reporting, ]

    def app_name(self, obj):
        return (obj.applications.app_name)

    def space_name(self, obj):
        return (obj.applications.spaces.space_name)

    def org_name(self, obj):
        return (obj.applications.spaces.orgs.org_name)


def nonpaassites_toggle_reporting(modeladmin, request, queryset):
    for site_name in queryset:
        if site_name.reporting_enabled:
            site_name.reporting_enabled = False
        else:
            site_name.reporting_enabled = True
        site_name.save()


nonpaassites_toggle_reporting.short_description = 'Toggle check enabled'


@admin.register(NonPaasSites)
class nonpaassites_admin(admin.ModelAdmin):
    list_display = ('id', 'site_name', 'site_url', 'is_protected', 'reporting_enabled')
    actions = [nonpaassites_toggle_reporting, ]
