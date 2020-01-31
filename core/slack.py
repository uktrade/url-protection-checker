from checker.models import ApplicationsItem, NonPaasSites
from django.conf import settings
import requests
import json


def non_paas_alert():
    open_site_list = ''
    sites_to_check = NonPaasSites.objects.filter(reporting_enabled=True)
    if sites_to_check.filter(is_protected=False):
        open_site_list += 'The following non PaaS sites are open\n'
        for site in sites_to_check:
            if site.is_protected is False:
                open_site_list += f'{site.site_url}\n'
        print(open_site_list)

        if settings.SLACK_ENABLED == 'True':
            print("Sending results to slack")
            url = f'{settings.SLACK_URL}/api/chat.postMessage'
            data = {'channel': f'{settings.SLACK_CHANNEL}', 'text': open_site_list}
            headers = {'Content-type': 'application/json; charset=utf-8',
                        'Authorization': f'Bearer {settings.SLACK_TOKEN}'}
            r = requests.post(url, data=json.dumps(data), headers=headers)


def daily_alert():
    slack_message = 'This is the daily url protection report.\n'
    urls_open = ''
    slack_report = ''

    count_routes_open = 0
    space_name = ''
    for app in ApplicationsItem.objects.filter(reporting_enabled=True):
        if app.is_protected is False:
            if space_name != app.applications.spaces.space_name:
                urls_open += f'\nSPACE: *{app.applications.spaces.space_name}*\n'
            urls_open += f'The Application: *{app.applications.app_name}* '
            # urls_open += f'in Space: {app.spaces.space_name} '
            urls_open += f'has the following route unprotected\n\t{app.app_route}\n'
            count_routes_open += 1
            space_name = app.applications.spaces.space_name
    slack_message += f'Number of routes open = {count_routes_open}'

    if count_routes_open != 0:
        slack_report = '```\n'
        slack_report += f'{urls_open}\n```'

    slack_report += f'\n```{slack_message}```\n'

    if settings.SLACK_ENABLED == 'True':
        print("Sending results to slack")
        url = f'{settings.SLACK_URL}/api/chat.postMessage'
        data = {'channel': f'{settings.SLACK_CHANNEL}', 'text': slack_report}
        headers = {'Content-type': 'application/json; charset=utf-8',
                    'Authorization': f'Bearer {settings.SLACK_TOKEN}'}
        r = requests.post(url, data=json.dumps(data), headers=headers)
        print(r.text)
        print(slack_report)

    non_paas_alert()
