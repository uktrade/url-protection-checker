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
    ApplicationsItem.objects.exclude(spaces_id__in=space_ids).delete()

    cf_token = cf_client._access_token

    for space_name, space_guid in Spaces.objects.values_list(
            'space_name',
            'space_guid').filter(check_enabled=True):

        for app in cf_client.v3.apps.list(space_guids=space_guid):
            Applications.objects.update_or_create(app_name=app['name'])

            response = requests.get(
                settings.CF_DOMAIN + '/v3/apps/' + app['guid'] + '/routes',
                params={},
                headers={'Authorization': f'Bearer {cf_token}'})
            route_data = response.json()

            for route in route_data['resources']:
                route_url = 'https://' + route['url']

                if 'apps.internal' not in route_url:
                    # breakpoint()
                    try:
                        response = requests.get(route_url)
                    except requests.exceptions.RequestException as e:
                        print(e)

                    if '<title>Access denied</title>' in str(response.content):
                        # print('Site is behind vpn')
                        ApplicationsItem.objects.update_or_create(
                            app_route=route_url,
                            defaults={
                                'applications_id': Applications.objects.get(
                                    app_name=app['name']).id,
                                'is_behind_vpn': True,
                                'spaces_id': Spaces.objects.get(space_name=space_name).id})

                    elif response.url.startswith(
                            'https://sso.trade.gov.uk') or response.url.startswith(
                            'http://sso.trade.uat.uktrade.io'):

                        # print('Site is behind Staff SSO')
                        ApplicationsItem.objects.update_or_create(
                            app_route=route_url,
                            defaults={
                                'applications_id': Applications.objects.get(
                                    app_name=app['name']).id,
                                'is_behind_sso': True,
                                'spaces_id': Spaces.objects.get(space_name=space_name).id})

                    else:
                        # print('Site is open')
                        ApplicationsItem.objects.update_or_create(
                            app_route=route_url,
                            defaults={
                                'applications_id': Applications.objects.get(
                                    app_name=app['name']).id,
                                'is_behind_vpn': False,
                                'is_behind_sso': False,
                                'spaces_id': Spaces.objects.get(space_name=space_name).id})
