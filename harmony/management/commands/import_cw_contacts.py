from django.core.management.base import BaseCommand
from harmony.models import ConnectWiseConfig, ConnectWiseCompany, ConnectWiseContact, SyncMapping
from harmony.utils import make_connectwise_api_call, log
import traceback

area = 'ConnectWise Contact Import'

class Command(BaseCommand):
    help = 'Import contacts from ConnectWise'

    def handle(self, *args, **kwargs):

        connectwise_configs = ConnectWiseConfig.objects.all()

        for connectwise_config in connectwise_configs:
            self.sync_contacts(connectwise_config)
                

    def sync_contacts(self, connectwise_config):
        # TODO:  Need to double-check this logic, this should delete contacts that no longer exist.
        try:
            sync_mappings = SyncMapping.objects.filter(connectwise_config=connectwise_config)
            contacts_to_sync = self.fetch_all_data(connectwise_config, 'company/contacts')
            scope_companies = []
            for contact in contacts_to_sync:
                try:
                    connectwise_company = ConnectWiseCompany.objects.get(
                        connectwise_config=connectwise_config,
                        connectwise_manage_id=contact.get('company', {}).get('id'),
                    )
                    if not scope_companies.__contains__(connectwise_company):
                        scope_companies.append(connectwise_company)
                        connectwise_contact, created = ConnectWiseContact.objects.get_or_create(
                        connectwise_company=connectwise_company,
                        connectwise_manage_id=contact.get('id'),
                        defaults={
                            "first_name": contact.get('firstName', ''),
                            "last_name": contact.get('lastName', '')
                        })
                        update_fields = []
                        if created:
                            if connectwise_contact.first_name != contact.get('firstName', ''):
                                connectwise_contact.first_name = contact.get('firstName', '')
                                update_fields.append('first_name')
                            if connectwise_contact.last_name != contact.get('lastName', ''):
                                connectwise_contact.last_name = contact.get('lastName', '')
                                update_fields.append('last_name')
                        if update_fields:
                            connectwise_contact.save(update_fields=update_fields)

                    # Delete out-of-scope contacts
                    for company in scope_companies:
                        contact_ids_to_sync = [contact['id'] for contact in contacts_to_sync]
                        contacts_to_delete = ConnectWiseContact.objects.filter(connectwise_company=company).exclude(connectwise_manage_id__in=contact_ids_to_sync)
                        contacts_to_delete.delete()
                except ConnectWiseCompany.DoesNotExist:
                    continue                
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