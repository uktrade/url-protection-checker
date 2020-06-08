import requests

from checker.models import NonPaasSites


def check_routes():
    # breakpoint()
    print('Checking non paas routes')
    sites_to_check = NonPaasSites.objects.filter(reporting_enabled=True)

    for site in sites_to_check:
        response = requests.get(site.site_url)
        print(site.site_url)

        if response.status_code == 401:
            print('Site ' + site.site_url + ' is protected')
            NonPaasSites.objects.update_or_create(
                site_url=site.site_url,
                defaults={'is_protected': True})
        else:
            print('Site ' + site.site_url + ' is not protected')
