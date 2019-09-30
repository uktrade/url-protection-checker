from django.core.management.base import BaseCommand
from core.cloudfoundry import cf_login, get_domains_list, find_open_routes
from core.slack import daily_alert


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Running Open Route Checker...')
        cf_client = cf_login()
        domains = get_domains_list(cf_client)
        find_open_routes(cf_client, domains)
        daily_alert()
