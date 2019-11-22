import requests

from cloudfoundry_client.client import CloudFoundryClient
from django.conf import settings

from checker.models import Spaces, Applications, ApplicationsItem


def cf_get_client(username, password, endpoint, http_proxy='', https_proxy=''):
    target_endpoint = endpoint
    proxy = dict(http=http_proxy, https=https_proxy)
    client = CloudFoundryClient(target_endpoint, proxy=proxy)
    client.init_with_user_credentials(username, password)
    return client


def cf_login():
    cf_client = cf_get_client(
        settings.CF_USERNAME,
        settings.CF_PASSWORD,
        settings.CF_DOMAIN)
    return cf_client


def find_open_routes(cf_client):
    # Check if space is enabled, if disabled delete records accisiated with that space.
    # This is needed if a space is no longer enabled.
    space_ids = Spaces.objects.filter(check_enabled=True).values_list('id', flat=True)
    Applications.objects.exclude(spaces_id__in=space_ids).delete()

    cf_token = cf_client._access_token

    for space_name, space_guid in Spaces.objects.values_list(
            'space_name',
            'space_guid').filter(check_enabled=True):

        # Delete apps from table that are no longer present.
        app_list = []
        response = requests.get(
            settings.CF_DOMAIN + '/v3/apps/',
            params={'space_guids': [space_guid, ]},
            headers={'Authorization': f'Bearer {cf_token}'})
        app_response = response.json()
        for app_item in app_response['resources']:
            app_list.append(app_item['name'])

        for app_in_table in Applications.objects.values('app_name').filter(
                spaces__space_name=space_name):
            if app_in_table['app_name'] not in app_list:
                Applications.objects.get(app_name=app_in_table['app_name']).delete()

        # Add new app or route to DB.
        for app in cf_client.v3.apps.list(space_guids=space_guid):
            Applications.objects.update_or_create(
                app_name=app['name'],
                defaults={
                    'spaces_id': Spaces.objects.get(space_name=space_name).id})

            response = requests.get(
                settings.CF_DOMAIN + '/v3/apps/' + app['guid'] + '/routes',
                params={},
                headers={'Authorization': f'Bearer {cf_token}'})
            route_data = response.json()
            # breakpoint()
            for route in route_data['resources']:
                route_url = 'https://' + route['url']
                print(route_url)
                if 'apps.internal' not in route_url:
                    try:
                        response = requests.get(route_url)
                        # print(response.url)
                        # print(response.status_code)
                    except requests.exceptions.RequestException as e:
                        print(e)

                    # Check if route works.
                    if not response.content.decode('utf-8').startswith(
                            '404 Not Found: Requested route'):
                        if '<title>Access denied</title>' in str(response.content):
                            # print('Site is behind vpn')
                            ApplicationsItem.objects.update_or_create(
                                app_route=route_url,
                                defaults={
                                    'applications_id': Applications.objects.get(
                                        app_name=app['name']).id,
                                    'is_behind_vpn': True, 'is_protected': True})

                        elif response.url.startswith(
                                'https://sso.trade.gov.uk') or response.url.startswith(
                                'https://sso.trade.uat.uktrade.io'):

                            # print('Site is behind Staff SSO')
                            ApplicationsItem.objects.update_or_create(
                                app_route=route_url,
                                defaults={
                                    'applications_id': Applications.objects.get(
                                        app_name=app['name']).id,
                                    'is_behind_sso': True, 'is_protected': True})

                        elif response.status_code == 401:
                            ApplicationsItem.objects.update_or_create(
                                app_route=route_url,
                                defaults={
                                    'applications_id': Applications.objects.get(
                                        app_name=app['name']).id,
                                    'is_behind_app_auth': True, 'is_protected': True})
                            # print('unauthourised')

                        else:
                            # print('Site is open')
                            ApplicationsItem.objects.update_or_create(
                                app_route=route_url,
                                defaults={
                                    'applications_id': Applications.objects.get(
                                        app_name=app['name']).id,
                                    'is_behind_vpn': False,
                                    'is_behind_sso': False,
                                    'is_behind_app_auth': False,
                                    'is_protected': False})
                    else:
                        try:
                            ApplicationsItem.objects.get(app_route=route_url).delete()
                        except ApplicationsItem.DoesNotExist:
                            pass
