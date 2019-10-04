import cowsay
import io
import random
from slacker import Slacker
from checker.models import ApplicationsItem
from django.conf import settings
from contextlib import redirect_stdout


cowsay_characters = cowsay.char_names


def hourly_alert():
    slack_message = 'This is the hourly url protection report.\n'
    count_routes_open = 0
    space_name = ''
    slack = Slacker(settings.SLACK_TOKEN)
    for app in ApplicationsItem.objects.filter(check_enabled=True):
        if app.is_behind_vpn is False and app.is_behind_sso is False:
            if space_name != app.applications.spaces.space_name:
                slack_message += f'\nSPACE: *{app.applications.spaces.space_name}*\n'
            slack_message += f'The Application: *{app.applications.app_name}* '
            # slack_message += f'in Space: {app.spaces.space_name} '
            slack_message += f'has the following route unprotected\n\t{app.app_route}\n'
            count_routes_open += 1
            space_name = app.applications.spaces.space_name
    if count_routes_open > 0:
        print(slack_message)
        # breakpoint()
        if settings.SLACK_ENABLED == 'True':
            print("Sending results to slack")
            slack.chat.post_message('#webops', slack_message)
    else:
        print('All good, no open routes')


def daily_alert():
    slack = Slacker(settings.SLACK_TOKEN)
    slack_message = 'This is the daily url protection report.\n'
    slack_report = ''
    cow_report = '```\n'
    count_routes_open = 0
    space_name = ''
    for app in ApplicationsItem.objects.filter(check_enabled=True):
        if app.is_behind_vpn is False and app.is_behind_sso is False:
            if space_name != app.applications.spaces.space_name:
                slack_report += f'\nSPACE: *{app.applications.spaces.space_name}*\n'
            slack_report += f'The Application: *{app.applications.app_name}* '
            # slack_report += f'in Space: {app.spaces.space_name} '
            slack_report += f'has the following route unprotected\n\t{app.app_route}\n'
            count_routes_open += 1
            space_name = app.applications.spaces.space_name
    slack_message += f'Number of routes open = {count_routes_open}'
    # Get a random cow say to spell out report to a string var.
    with io.StringIO() as buf, redirect_stdout(buf):
        getattr(cowsay, random.choice(cowsay_characters))(slack_message)
        cow_report += buf.getvalue()
    # breakpoint()
    cow_report += f'```\n```\n{slack_report}\n```'
    print(cow_report)
    if settings.SLACK_ENABLED == 'True':
        print("Sending results to slack")
        slack.chat.post_message('#webops', cow_report)
