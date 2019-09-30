from slacker import Slacker
from checker.models import ApplicationsItem
from django.conf import settings


def raise_alerts():
    # breakpoint()
    slack = Slacker(settings.SLACK_TOKEN)

    count_routes_open = 0
    for app in ApplicationsItem.objects.filter(check_enabled=True):
        if app.is_behind_vpn is False and app.is_behind_sso is False:
            print(f'The Application: {app.applications.app_name} '
                  f'in Space: {app.spaces.space_name} has the following route unprotected')
            print(f'\t{app.app_route}')
            count_routes_open += 1
    print(f'Number of routes open: {count_routes_open}')
    # slack.chat.post_message('#webops', 'This is a test from JP')
