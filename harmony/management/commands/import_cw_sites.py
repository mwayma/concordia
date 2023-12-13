from django.core.management.base import BaseCommand
from harmony.models import ConnectWiseConfig, ConnectWiseCompany, ConnectWiseSite
from harmony.utils import make_connectwise_api_call, log
import traceback
area = 'ConnectWise Site Import'

class Command(BaseCommand):
    help = 'Import sites from ConnectWise'

    def handle(self, *args, **kwargs):
        try:
            connectwise_configs = ConnectWiseConfig.objects.all()

            for connectwise_config in connectwise_configs:
                companies = ConnectWiseCompany.objects.filter(connectwise_config=connectwise_config)
                for company in companies:
                    company_id = company.connectwise_manage_id
                    next_page_url = 'initial_value'
                    endpoint = f'company/companies/{company_id}/sites'
                    page_number = 1
                    sites = []
                    while next_page_url:
                        # Make the API call
                        response_data, next_page_url = make_connectwise_api_call(connectwise_config, endpoint, params={'page': page_number})
                        page_number += 1
                        sites.extend(response_data)
                    for site in sites:
                        site_mapping, created = ConnectWiseSite.objects.get_or_create(
                        company=company,
                        connectwise_manage_id=site['id'],
                        defaults={
                            'connectwise_manage_name': site['name']
                        }
                    )
                    if created and site_mapping.connectwise_manage_name != site['name']:
                        site_mapping.connectwise_manage_name=site['name']
                        site_mapping.save()
                
                # Delete deleted sites
                site_ids_to_sync = [site['id'] for site in sites]
                sites_to_delete = ConnectWiseSite.objects.filter(company=company).exclude(connectwise_manage_id__in=site_ids_to_sync)
                sites_to_delete.delete()

        except Exception as e:
            message = f'An error occurred while syncing Sites: {e}\n{traceback.format_exc()}'
            log('error', area, message)
            self.stdout.write(self.style.ERROR(message))