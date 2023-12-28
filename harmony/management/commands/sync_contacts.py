from django.core.management.base import BaseCommand
from harmony.models import ConnectWiseConfig, CompanyMapping, ConnectWiseSite, ConnectWiseCompany
from harmony.utils import make_connectwise_api_call, log
from harmony.connectwise import *
from harmony.dataverse import *

### Version 1 is a one-way sync from ConnectWise to Dataverse.  This is for creating a new environment, not for an existing one with duplicate data.  Create new Accounts and Contacts if none are locally mapped in the database.
### Attempt to map the new CustomerAddress to a ConnectWise Site.  

class Command(BaseCommand):

    def create_unsynced_dataverse_contacts(self):
        # Get all SyncMapping instances
        sync_mappings = SyncMapping.objects.all()

        for sync_mapping in sync_mappings:
            # Get all ConnectWiseContact instances not in ContactMapping for the current SyncMapping
            unsynced_connectwise_contacts = ConnectWiseContact.objects.exclude(
                id__in=ContactMapping.objects.filter(sync_mapping=sync_mapping).values_list('connectwise_contact__id', flat=True)
            )

            # Iterate through unsynced ConnectWiseContact instances and create Dataverse contacts
            for connectwise_contact in unsynced_connectwise_contacts:
                dataverse_account = CompanyMapping.objects.get(sync_mapping=sync_mapping, connectwise_company=connectwise_contact.connectwise_company).dataverse_account
                #Get ConnectWise JSON object
                contact_json = get_connectwise_contact(connectwise_contact=connectwise_contact)
                # Create Dataverse contact and update ContactMapping
                create_dataverse_contact(sync_mapping, dataverse_account, connectwise_contact_data=contact_json)

    def handle(self, *args, **kwargs):
        self.create_unsynced_dataverse_contacts()