from django.core.management.base import BaseCommand
from harmony.models import ConnectWiseConfig, ConnectWiseCompany
from harmony.utils import make_connectwise_api_call, log
import traceback

class Command(BaseCommand):
    help = 'Import companies from ConnectWise'

    def handle(self, *args, **kwargs):

        connectwise_configs = ConnectWiseConfig.objects.all()

        for connectwise_config in connectwise_configs:

            sync_company_types = connectwise_config.get_sync_company_types_list()
            sync_company_statuses = connectwise_config.get_sync_company_statuses_list()

            if sync_company_types or sync_company_statuses:
                self.sync_companies_filter(connectwise_config, sync_company_types, sync_company_statuses)

            # Assume there is no filter and we want ALL companies
            if not sync_company_types and not sync_company_statuses:
                self.sync_companies(connectwise_config)

    def sync_companies(self, connectwise_config):
        try:
            companies_to_sync = self.fetch_all_data(connectwise_config, 'company/companies')
            for company in companies_to_sync:
                company_mapping, created = ConnectWiseCompany.objects.get_or_create(
                    connectwise_config=connectwise_config,
                    connectwise_manage_id=company['id'],
                )
                if created and company_mapping.connectwise_manage_name != company['name']:
                    company_mapping.connectwise_manage_name=company['name']
                    company_mapping.save()
                if not created:
                    company_mapping.connectwise_manage_name=company['name']
                    company_mapping.save()
            
            # Delete out-of-scope companies
            company_ids_to_sync = [company['id'] for company in companies_to_sync]
            companies_to_delete = ConnectWiseCompany.objects.filter(connectwise_config=connectwise_config).exclude(connectwise_manage_id__in=company_ids_to_sync)
            companies_to_delete.delete()


        except Exception as e:
            message = f'An error occurred while syncing Companies: {e}\n{traceback.format_exc()}'
            log('error', 'ConnectWise Import', message)
            self.stdout.write(self.style.ERROR(message))
    
    def sync_companies_filter(self, connectwise_config, sync_company_types, sync_company_statuses):
        try:
            # Build the list of types to filter against, if there are any.  Make the API call to CompanyTypeAssociations and get a list of matching company IDs
            companies_by_type = []
            if sync_company_types:
                next_page_url = 'initial_value'
                endpoint = 'company/companyTypeAssociations'
                # List of conditions
                conditions_list = [f'type/id={type_obj.connectwise_manage_id}' for type_obj in sync_company_types]
                conditions_query = ' or '.join(conditions_list)
                page_number = 1
                while next_page_url:
                    # Make the API call
                    response_data, next_page_url = make_connectwise_api_call(connectwise_config, endpoint, params={'conditions' : conditions_query, 'pageSize': 1000, 'page': page_number})
                    page_number += 1
                    companies_by_type.extend(response_data)

            # Build the list of statuses to filter against, if there are any.  Make the API call to Companies and get a list of matching company objects.
            companies_by_status = []
            if sync_company_statuses:
                next_page_url = 'initial_value'
                endpoint = 'company/companies'
                conditions_list = [f'status/id={status_obj.connectwise_manage_id}' for status_obj in sync_company_statuses]
                conditions_query = ' or '.join(conditions_list)
                page_number = 1
                while next_page_url:
                    # Make the API call
                    response_data, next_page_url = make_connectwise_api_call(connectwise_config, endpoint, params={'conditions' : conditions_query, 'pageSize': 1000, 'page': page_number})
                    page_number += 1
                    companies_by_status.extend(response_data)

            # Compare the two lists and only keep company objects that are in both lists.  If there's only one list then obviously we go with that.
            companies_to_sync = []
            if sync_company_types and sync_company_statuses:
                # Find common elements based on the "id" attribute
                common_ids_status = set(company['id'] for company in companies_by_status)
                common_ids_type = set(company['company']['id'] for company in companies_by_type)

                # Find common IDs by taking the intersection of both sets
                common_ids = common_ids_status & common_ids_type

                # Filter companies_by_status to keep only the common elements
                companies_by_status_common = [company for company in companies_by_status if company['id'] in common_ids]
                companies_to_sync.extend(companies_by_status_common)
            else:
                if sync_company_types:
                    nested_companies_by_type = [company['company'] for company in companies_by_type]
                    companies_to_sync.extend(nested_companies_by_type)
                if sync_company_statuses:
                    companies_to_sync.extend(companies_by_status)
            
            # Sync companies
            for company in companies_to_sync:
                company_mapping, created = ConnectWiseCompany.objects.get_or_create(
                    connectwise_config=connectwise_config,
                    connectwise_manage_id=company['id'],
                )
                if created and company_mapping.connectwise_manage_name != company['name']:
                    company_mapping.connectwise_manage_name=company['name']
                    company_mapping.save()
                if not created:
                    company_mapping.connectwise_manage_name=company['name']
                    company_mapping.save()
            
            # Delete out-of-scope companies
            company_ids_to_sync = [company['id'] for company in companies_to_sync]
            companies_to_delete = ConnectWiseCompany.objects.filter(connectwise_config=connectwise_config).exclude(connectwise_manage_id__in=company_ids_to_sync)
            companies_to_delete.delete()


        except Exception as e:
            message = f"An error occurred while syncing Companies by filter: {str(e)}"
            log('error', 'ConnectWise Import', message)
            self.stdout.write(self.style.ERROR(message))

    def fetch_all_data(self, connectwise_config, endpoint):
        data = []
        next_page_url = 'initial_value'
        page_number = 1
        while next_page_url:
            # Make the API call
            response_data, next_page_url = make_connectwise_api_call(connectwise_config, endpoint, params={'pageSize': 1000, 'page': page_number})
            page_number += 1
            data.extend(response_data)

        return data