from django.core.management.base import BaseCommand
from core.cloudfoundry import cf_login, find_open_routes
from core.slack import hourly_alert


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Running Open Route Checker...')
        cf_client = cf_login()
        find_open_routes(cf_client)
        hourly_alert()
