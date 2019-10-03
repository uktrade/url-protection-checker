from django.core.management.base import BaseCommand
from core.cloudfoundry import cf_get_client
from django.conf import settings

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
        space_list = {}

        for space in cf_client.v3.spaces.list(organization_guids=settings.ORG_GUID):
            print(space['name'])
            print(space['guid'])
            space_list[space['name']] = space['guid']
        print(space_list)

        # breakpoint()
        for space, guid in space_list.items():
            Spaces.objects.update_or_create(space_name=space, space_guid=guid)
