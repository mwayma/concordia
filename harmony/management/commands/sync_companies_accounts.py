from django.core.management.base import BaseCommand
from harmony.models import ConnectWiseConfig, CompanyMapping, ConnectWiseSite, ConnectWiseCompany
from harmony.utils import make_connectwise_api_call, log
from harmony.connectwise import *
from harmony.dataverse import *

### Version 1 is a one-way sync from ConnectWise to Dataverse.  This is for creating a new environment, not for an existing one with duplicate data.  Create new Accounts and Contacts if none are locally mapped in the database.
### Attempt to map the new CustomerAddress to a ConnectWise Site.  

class Command(BaseCommand):

    def get_unsynced_connectwise_companies(self):
        # Get all SyncMappings
        sync_mappings = SyncMapping.objects.all()

        unsynced_companies = {}

        # Iterate through each SyncMapping
        for sync_mapping in sync_mappings:
            # Get the ConnectWiseCompany objects associated with the SyncMapping
            connectwise_companies = ConnectWiseCompany.objects.filter(connectwise_config=sync_mapping.connectwise_config)

            # Exclude companies that are already mapped to a DataverseAccount
            mapped_companies = CompanyMapping.objects.filter(connectwise_company__in=connectwise_companies).values_list('connectwise_company__id', flat=True)
            unsynced_companies[sync_mapping.id] = connectwise_companies.exclude(id__in=mapped_companies)

        return unsynced_companies

    def synchronize_connectwise_companies(self):
        unsynced_companies = self.get_unsynced_connectwise_companies()

        for sync_mapping_id, connectwise_companies in unsynced_companies.items():
            sync_mapping = SyncMapping.objects.get(id=sync_mapping_id)

            for connectwise_company in connectwise_companies:
                # Retrieve ConnectWise Company JSON object
                endpoint = f'company/companies/{connectwise_company.connectwise_manage_id}'
                company_json = make_connectwise_api_call(endpoint=endpoint, connectwise_config=sync_mapping.connectwise_config)

                # Create Dataverse account
                create_dataverse_account(sync_mapping, company_json)

    def update_connectwise_companies(self):
        # Get all CompanyMapping instances
        company_mappings = CompanyMapping.objects.all()

        for company_mapping in company_mappings:
            connectwise_company = company_mapping.connectwise_company
            # Check if names are different
            if connectwise_company.connectwise_manage_name != company_mapping.dataverse_account.dataverse_name:
                # Retrieve ConnectWise Company JSON object
                endpoint = f'company/companies/{connectwise_company.connectwise_manage_id}'
                company_json = make_connectwise_api_call(endpoint=endpoint, connectwise_config=company_mapping.sync_mapping.connectwise_config)
                # Update Dataverse account
                dataverse_account = DataverseAccount.objects.get(id=company_mapping.dataverse_account.id)
                edit_dataverse_account(dataverse_account, connectwise_company_data=company_json)

    def handle(self, *args, **kwargs):
        self.synchronize_connectwise_companies()
        self.update_connectwise_companies()