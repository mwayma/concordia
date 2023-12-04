from django.core.management.base import BaseCommand
from harmony.models import ConnectWiseConfig, ConnectWiseCompany, ConnectWiseContact, ContactMapping
from harmony.utils import make_connectwise_api_call, log
from harmony.dataverse import create_dataverse_contact, edit_dataverse_contact
import traceback
area = 'ConnectWise Contact Import'

class Command(BaseCommand):
    help = 'Import contacts from ConnectWise'

    def handle(self, *args, **kwargs):

        connectwise_configs = ConnectWiseConfig.objects.all()

        for connectwise_config in connectwise_configs:
            self.sync_contacts(connectwise_config)
                

    def sync_contacts(self, connectwise_config):
        # TODO:  Create new Dataverse Contact if it doesn't exist.  Edit Dataverse Contact if there is a change in name.
        try:
            contacts_to_sync = self.fetch_all_data(connectwise_config, 'company/contacts')
            for contact in contacts_to_sync:
                connectwise_company = ConnectWiseCompany.objects.get(
                    connectwise_config=connectwise_config,
                    connectwise_manage_id=contact.get('company', {}).get('id'),
                )
                if connectwise_company:
                    connectwise_contact, created = ConnectWiseContact.objects.get_or_create(
                        connectwise_company=connectwise_company,
                        connectwise_manage_id=contact.get('id'),
                    )
                    if not created or (connectwise_contact.first_name != contact['firstName'] or connectwise_contact.last_name != contact['lastName']):                                
                        connectwise_contact.first_name = contact['firstName']
                        connectwise_contact.last_name = contact['lastName']
                        connectwise_contact.connectwise_manage_id=contact.get('id')
                        connectwise_contact.save()
                    # Delete out-of-scope contacts
                    contact_ids_to_sync = [contact['id'] for contact in contacts_to_sync]
                    contacts_to_delete = ConnectWiseContact.objects.filter(connectwise_company=connectwise_company).exclude(connectwise_manage_id__in=contact_ids_to_sync)
                    contacts_to_delete.delete()
                
        except Exception as e:
            message = f'An error occurred while syncing Contacts: {e}\n{traceback.format_exc()}'
            log('error', area, message)
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