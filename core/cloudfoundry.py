import requests

from cloudfoundry_client.client import CloudFoundryClient
from django.conf import settings
from itertools import chain

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


def get_domains_list(cf_client):
    domains = {}
    for domain in chain(cf_client.v2.private_domains.list(),
                        cf_client.v2.shared_domains.list()):
        domains[domain['metadata']['guid']] = domain['entity']['name']
    return (domains)


def find_open_routes(cf_client, domains):
    # Check if space is enabled, if disabled delete records accisiated with that space.
    # This is needed if a space is no longer enabled.
    # breakpoint()
    space_ids = Spaces.objects.filter(check_enabled=True).values_list('id', flat=True)
    ApplicationsItem.objects.exclude(spaces_id__in=space_ids).delete()

    for space_name, space_guid in Spaces.objects.values_list(
            'space_name',
            'space_guid').filter(check_enabled=True):
        # print(space_name)
        for app in cf_client.v3.apps.list(space_guids=space_guid):
            # print(app['name'])
            Applications.objects.update_or_create(app_name=app['name'])
            # breakpoint()
            for route in app.route_mappings():
                route_mapping = route.route()
                domain = domains[route_mapping['entity']['domain_guid']]
                path = route_mapping['entity']['path']
                host = route_mapping['entity']['host']
                # print(f'https://{host}.{domain}/{path}')
                # icheck if host was defined.
                if host:
                    route_url = f'https://{host}.{domain}/{path}'
                else:
                    route_url = f'https://{domain}/{path}'

                if domain != 'apps.internal':
                    response = requests.get(route_url)
                    # breakpoint()
                    if '<title>Access denied</title>' in str(response.content):
                        # print('Site is behind vpn')
                        ApplicationsItem.objects.update_or_create(
                            app_route=route_url,
                            defaults={
                                'applications_id': Applications.objects.get(
                                    app_name=app['name']).id,
                                'is_behind_vpn': True,
                                'spaces_id': Spaces.objects.get(space_name=space_name).id})

                    elif 'https://sso.trade.gov.uk/saml2/login' in response.url:
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
                                'spaces_id': Spaces.objects.get(space_name=space_name).id})
