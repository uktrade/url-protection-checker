import requests
import json

from cloudfoundry_client.client import CloudFoundryClient
from django.conf import settings

from checker.models import Spaces, Applications, ApplicationsItem


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


def cf_get_client(username, password, endpoint, http_proxy="", https_proxy=""):
    target_endpoint = endpoint
    proxy = dict(http=http_proxy, https=https_proxy)
    client = CloudFoundryClient(target_endpoint, proxy=proxy)
    client.init_with_user_credentials(username, password)
    return client


def cf_login():
    cf_client = cf_get_client(settings.CF_USERNAME, settings.CF_PASSWORD, settings.CF_DOMAIN)
    return cf_client


def get_spaces_no_ip_filter(cf_client):
    cf_token = cf_client._access_token
    #breakpoint()
    #Only run if space is enabled and there is no filter in this space (filter_guid=-1)
    for space_obj in Spaces.objects.filter(check_enabled=True,filter_guid=-1):
        #Only auto-bind in orgs that are listed (eg, might not want to bind prod org)
        if not space_obj.orgs.org_name in settings.EXCLUDE_ORG_AUTO_FILTER_SERVICE:
            print(f"{bcolours.WARNING}{space_obj.space_name} space has no ip filter.  Creating IP Filter{bcolours.ENDC}")
            if settings.AUTO_CREATE_IP_FILTER_ENABLED:
                json_data = {
                    'type': 'user-provided',
                    'name': 'ip-filter-service',
                    'route_service_url': f'{settings.FILTER_URL}',
                    'relationships': {
                        'space': {
                            'data': {
                                'guid': space_obj.space_guid
                            }
                        },
                    }
                }

                response = requests.post(
                    settings.CF_DOMAIN + "/v3/service_instances",
                    headers={"Authorization": f"Bearer {cf_token}", "Content-Type": "application/json"},
                    data=json.dumps(json_data),
                )
                #breakpoint()
                service_response = response.json()
                #Add new service to DB
                space_obj.filter_guid = service_response['guid']
                space_obj.save()
            else:
                print(f"{bcolours.OKCYAN}IP Filter not created running in test mode{bcolours.ENDC}")



def find_open_routes(cf_client):
    # Check if space is enabled, if disabled delete records accisiated with that space.
    # This is needed if a space is no longer enabled.
    space_ids = Spaces.objects.filter(check_enabled=True).values_list("id", flat=True)
    Applications.objects.exclude(spaces_id__in=space_ids).delete()

    cf_token = cf_client._access_token

    for space_name, space_guid in Spaces.objects.values_list("space_name", "space_guid").filter(check_enabled=True):

        # Delete apps from table that are no longer present.
        app_list = []
        response = requests.get(
            settings.CF_DOMAIN + "/v3/apps/",
            params={"space_guids": [space_guid,]},
            headers={"Authorization": f"Bearer {cf_token}"},
        )
        app_response = response.json()
        for app_item in app_response["resources"]:
            app_list.append(app_item["name"])

        for app_in_table in Applications.objects.values("app_name").filter(spaces__space_name=space_name):
            if app_in_table["app_name"] not in app_list:
                Applications.objects.get(app_name=app_in_table["app_name"]).delete()

        # Add new app or route to DB.
        for app in cf_client.v3.apps.list(space_guids=space_guid):
            Applications.objects.update_or_create(
                app_name=app["name"], defaults={"spaces_id": Spaces.objects.get(space_guid=space_guid).id}
            )

            response = requests.get(
                settings.CF_DOMAIN + "/v3/apps/" + app["guid"] + "/routes",
                params={},
                headers={"Authorization": f"Bearer {cf_token}"},
            )
            route_data = response.json()

            # Delete routes from table that have now been removed from app.
            list_of_routes = []
            for route in route_data["resources"]:
                list_of_routes.append(f"https://{route['url']}")
            for route_to_check in ApplicationsItem.objects.values_list("app_route", flat=True).filter(
                applications__app_name=app["name"]
            ):
                if route_to_check not in list_of_routes:
                    print(f"deleting this route: {route_to_check}")
                    ApplicationsItem.objects.get(app_route=route_to_check).delete()

            # Add/Update routes and check if protected.
            for route in route_data["resources"]:
                route_url = "https://" + route["url"]
                print(route_url)
                if "apps.internal" not in route_url:
                    try:
                        response = requests.get(route_url)

                    except requests.exceptions.RequestException as e:
                        print(e)
                        response._content = b'<small>unknown_route</small>'

                    #breakpoint()
                    # Check if route works.
                    if not "<small>unknown_route</small>" in str(response.content):
                        # Check for non-prod IP filter
                        if "<title>Access denied</title>" in str(response.content):
                            # print('Site is behind vpn')
                            ApplicationsItem.objects.update_or_create(
                                app_route=route_url,
                                defaults={
                                    "applications_id": Applications.objects.get(app_name=app["name"]).id,
                                    "is_behind_vpn": True,
                                    "is_protected": True,
                                    "route_guid": route["guid"],
                                },
                            )

                        elif response.url.startswith("https://sso.trade.gov.uk") or response.url.startswith(
                            "https://sso.trade.uat.uktrade.io"
                        ):

                            # print('Site is behind Staff SSO')
                            ApplicationsItem.objects.update_or_create(
                                app_route=route_url,
                                defaults={
                                    "applications_id": Applications.objects.get(app_name=app["name"]).id,
                                    "is_behind_sso": True,
                                    "is_protected": True,
                                    "route_guid": route["guid"],
                                },
                            )

                        # Check for basic Auth
                        elif response.status_code == 401:
                            ApplicationsItem.objects.update_or_create(
                                app_route=route_url,
                                defaults={
                                    "applications_id": Applications.objects.get(app_name=app["name"]).id,
                                    "is_behind_app_auth": True,
                                    "is_protected": True,
                                    "route_guid": route["guid"],
                                },
                            )

                        # Check for prod IP filter
                        elif response.status_code == 403:
                            ApplicationsItem.objects.update_or_create(
                                app_route=route_url,
                                defaults={
                                    "applications_id": Applications.objects.get(app_name=app["name"]).id,
                                    "is_behind_vpn": True,
                                    "is_protected": True,
                                    "route_guid": route["guid"],
                                },
                            )
                            # print('unauthourised')

                        else:
                            # print('Site is open')
                            # breakpoint()
                            ApplicationsItem.objects.update_or_create(
                                app_route=route_url,
                                defaults={
                                    "applications_id": Applications.objects.get(app_name=app["name"]).id,
                                    "is_behind_vpn": False,
                                    "is_behind_sso": False,
                                    "is_behind_app_auth": False,
                                    "is_protected": False,
                                    "route_guid": route["guid"],
                                },
                            )
                    else:
                        try:
                            ApplicationsItem.objects.get(app_route=route_url).delete()
                        except ApplicationsItem.DoesNotExist:
                            pass


def lock_unprotected(cf_client):
    # breakpoint()
    slack_report = ''
    cf_token = cf_client._access_token

    for app_item in ApplicationsItem.objects.filter(is_protected='False',  reporting_enabled='True'):
        print(f"Route is open to public: {bcolours.WARNING}{app_item.app_route}\nBinding {app_item.app_route} to IP Filter{bcolours.ENDC}")
        slack_report += f"Route was open to public: {app_item.app_route}"
        json_data = {
            'relationships': {
                'route': {
                    'data': {
                        'guid': app_item.route_guid
                    }
                },
                'service_instance': {
                    'data': {
                        'guid': app_item.applications.spaces.filter_guid
                        }
                }
            }
        }
        if settings.BIND_ENABLED == 'True' and app_item.applications.spaces.filter_guid !=  '-1':
            response = requests.post(
                settings.CF_DOMAIN + "/v3/service_route_bindings",
                headers={"Authorization": f"Bearer {cf_token}", "Content-Type": "application/json"},
                data=json.dumps(json_data),
            )
            # breakpoint()
            bind_response = response.json()
            print(bind_response['last_operation']['state'])
            print(f"{bcolours.OKGREEN}{app_item.app_route} is now bound to IP Filter{bcolours.ENDC}")
            slack_report += f"\nThis route has now been bound to IP filter\n"
            app_item.is_behind_vpn = True
            app_item.is_protected = True
            app_item.save()
        else:
            print(f"{bcolours.OKCYAN}{app_item.app_route} will NOT be bound{bcolours.ENDC}")

    return slack_report
