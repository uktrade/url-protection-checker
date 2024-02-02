from django.core.management.base import BaseCommand
from core.cloudfoundry import cf_get_client
from django.conf import settings

import requests

from checker.models import Spaces, Orgs

class bcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_ip_filter_guid(cf_token, space_guid):
    #if no filter is found then the filter guid is left at -1
    filter_guid = "-1"

    print(f"{bcolours.OKCYAN}Getting guid for ip-filter{bcolours.ENDC}")
    response = requests.get(
        settings.CF_DOMAIN + "/v3/service_instances",
        params={"space_guids": [space_guid, ]},
        headers={"Authorization": f"Bearer {cf_token}"},
    )
    service_response = response.json()
    for service in service_response["resources"]:

        if service["name"] == "ip-filter-service":
            filter_guid = service["guid"]

    return filter_guid


def load_spaces():
    print('Running')
    cf_client = cf_get_client(
        settings.CF_USERNAME,
        settings.CF_PASSWORD,
        settings.CF_DOMAIN)

    cf_token = cf_client._access_token

    orgs_list = {}

    for org in cf_client.v3.organizations.list():
        print(f"{bcolours.OKBLUE}{org['name']}{bcolours.ENDC}")
        orgs_list[org['name']] = org['guid']

    for org, org_guid in orgs_list.items():
        Orgs.objects.update_or_create(org_name=org, org_guid=org_guid)

        for space in cf_client.v3.spaces.list(organization_guids=org_guid):
            print(f"{bcolours.OKGREEN}{space['name']}{bcolours.ENDC}")
            filter_guid = get_ip_filter_guid(cf_token, space['guid'])
            # breakpoint()
            Spaces.objects.update_or_create(
                space_guid=space['guid'], defaults={
                    'space_name': space['name'],
                    'filter_guid': filter_guid,
                    'orgs': Orgs.objects.get(org_guid=org_guid)
                    }
                )



class Command(BaseCommand):


    def handle(self, *args, **options):

        load_spaces()
