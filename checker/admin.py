from django.contrib import admin
from .models import Orgs, Spaces, ApplicationsItem, NonPaasSites


from django.forms import ValidationError, ModelForm


class CheckForm(ModelForm):
    class Meta:
        model = ApplicationsItem
        exclude = []

    def clean(self):
        data = super().clean()
        if not data['reporting_enabled'] and not data['reporting_disabled_reason']:
            raise ValidationError('You need to supply a reason why report is disabled')

        return data


class modeladmin(admin.ModelAdmin):
    form = CheckForm


def toggle_space(orgs_id, check):
    #breakpoint()
    for space_obj in Spaces.objects.filter(orgs_id=orgs_id):
        space_obj.check_enabled = check
        space_obj.save()


def org_toggle_enabled(modeladmin, request, queryset):
    for org in queryset:
        if org.check_enabled:
            org.check_enabled = False
            toggle_space(org.id, False)
        else:
            org.check_enabled = True
            toggle_space(org.id, True)
        org.save()


org_toggle_enabled.short_description = 'Toggle check enabled'


@admin.register(Orgs)
class org_admin(admin.ModelAdmin):
    list_display = ('id', 'org_name', 'org_guid', 'check_enabled')
    actions = [org_toggle_enabled, ]


def space_toggle_enabled(modeladmin, request, queryset):
    for space_name in queryset:
        if space_name.check_enabled:
            space_name.check_enabled = False
        else:
            space_name.check_enabled = True
        space_name.save()


space_toggle_enabled.short_description = 'Toggle check enabled'


@admin.register(Spaces)
class space_admin(admin.ModelAdmin):
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
    form = CheckForm
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

    list_filter = ('reporting_enabled', 'is_protected')

    search_fields = ['applications__app_name',
                        'applications__spaces__orgs__org_name',
                        'applications__spaces__space_name']

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
