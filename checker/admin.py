from django.contrib import admin

from .models import Spaces, ApplicationsItem


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


def toggle_enabled(modeladmin, request, queryset):
    for app_route in queryset:
        if app_route.check_enabled:
            app_route.check_enabled = False
        else:
            app_route.check_enabled = True
        app_route.save()


toggle_enabled.short_description = 'Toggle check enabled'


@admin.register(ApplicationsItem)
class applicationsitem_admin(admin.ModelAdmin):
    list_display = ('id',
                    'space_name',
                    'app_name',
                    'app_route',
                    'is_behind_vpn',
                    'is_behind_sso',
                    'check_enabled')
    actions = [toggle_enabled, ]

    def app_name(self, obj):
        return (obj.applications.app_name)

    def space_name(self, obj):
        return (obj.applications.spaces.space_name)
