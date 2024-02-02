from django.core.management.base import BaseCommand
from core.cloudfoundry import cf_login, find_open_routes, lock_unprotected, get_spaces_no_ip_filter
from core.slack import daily_alert
from core.check_non_paas_sites import check_routes
from .load_spaces_db import load_spaces
from datetime import datetime
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        cf_client = cf_login()
        #breakpoint()
        #Once a day check for any spaces without ip-filter-service
        current_time = datetime.now()
        if current_time.hour == int(settings.LOAD_DB_HOUR):
            print(f"Current hour {current_time.hour}")
            load_spaces()

        get_spaces_no_ip_filter(cf_client)

        #Now check all open routes
        print('Running Open Route Checker...')

        find_open_routes(cf_client)
        check_routes()
        slack_report = lock_unprotected(cf_client)
        daily_alert(slack_report)
