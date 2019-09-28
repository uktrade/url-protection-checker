import json
import requests

from django.core.management.base import BaseCommand
from core.cloudfoundry import cf_get_client
from django.conf import settings
from itertools import chain

from checker.models import Spaces

class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Running')
        # breakpoint()
        cf_client = cf_get_client(
            settings.CF_USERNAME,
            settings.CF_PASSWORD,
            settings.CF_DOMAIN)
        # breakpoint()

        domains = {}

        for domain in chain(cf_client.v2.private_domains.list(),
                            cf_client.v2.shared_domains.list()):
            domains[domain['metadata']['guid']] = domain['entity']['name']
        # breakpoint()
        for space_name, space_guid in Spaces.objects.values_list('space_name', 'space_guid').filter(enabled=True):
            print(space_name)

            for app in cf_client.v3.apps.list(space_guids=space_guid):
                print(app['name'])

                # breakpoint()
                for route in app.route_mappings():
                    route_mapping = route.route()
                    domain = domains[route_mapping['entity']['domain_guid']]

                    path = route_mapping['entity']['path']
                    host = route_mapping['entity']['host']
                    print(f'https://{host}.{domain}/{path}')
                    route_url = f'https://{host}.{domain}/{path}'

                    if domain != 'apps.internal':
                        response = requests.get(route_url)
                        # breakpoint()
                        if '<title>Access denied</title>' in str(response.content):
                            print('Site is behind vpn')

                        else:
                            print('Site is open')
