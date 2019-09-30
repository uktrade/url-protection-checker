from django.contrib import admin

from .models import Spaces, ApplicationsItem


@admin.register(Spaces)
class service_admin(admin.ModelAdmin):
    list_display = ('id', 'space_name', 'space_guid', 'check_enabled')


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
                    'get_space_name',
                    'get_app_name',
                    'app_route',
                    'is_behind_vpn',
                    'is_behind_sso',
                    'check_enabled')
    actions = [toggle_enabled, ]

    def get_app_name(self, obj):
        return (obj.applications.app_name)

    def get_space_name(self, obj):
        return (obj.spaces.space_name)
