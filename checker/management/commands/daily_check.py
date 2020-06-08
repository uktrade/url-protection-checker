from django.core.management.base import BaseCommand
from core.cloudfoundry import cf_login, find_open_routes
from core.slack import daily_alert
from core.check_non_paas_sites import check_routes


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Running Open Route Checker...')
        cf_client = cf_login()
        find_open_routes(cf_client)
        check_routes()
        daily_alert()
