from django.core.management.base import BaseCommand
from harmony.models import ConnectWiseConfig, CompanyType, CompanyStatus
from harmony.utils import make_connectwise_api_call

class Command(BaseCommand):
    help = 'Import company types and statuses from ConnectWise'

    def handle(self, *args, **kwargs):
        # Fetch ConnectWiseConfig instances
        connectwise_configs = ConnectWiseConfig.objects.all()

        for connectwise_config in connectwise_configs:
            # Fetch data from ConnectWise API (modify the endpoint as needed)
            company_types_data = make_connectwise_api_call(connectwise_config, 'company/companies/types', method='get')
            company_statuses_data = make_connectwise_api_call(connectwise_config, 'company/companies/statuses', method='get')

            # Process and create/update CompanyType and CompanyStatus records
            self.sync_company_types(connectwise_config, company_types_data)
            self.sync_company_statuses(connectwise_config, company_statuses_data)

    def sync_company_types(self, connectwise_config, data):
        try:
            # Process and create/update CompanyType records
            for item in data:
                connectwise_manage_id = item.get('id')
                company_type_name = item.get('name')
                vendor_flag = item.get('vendor_flag', False)
                inactive_flag = item.get('inactiveFlag')

                if not inactive_flag:
                    # Try to get an existing CompanyType record
                    company_type, created = CompanyType.objects.get_or_create(
                        connectwise_config=connectwise_config,
                        connectwise_manage_id=connectwise_manage_id,
                        defaults={'name': company_type_name, 'vendor_flag': vendor_flag}
                    )

                # Update the existing record if it already exists
                if not created:
                    company_type.name = company_type_name
                    company_type.vendor_flag = vendor_flag
                    company_type.save()
                    
            # Remove any existing records not present in the ConnectWise response
            CompanyType.objects.filter(connectwise_config=connectwise_config).exclude(connectwise_manage_id__in=[item['id'] for item in data]).delete()

            # Extract IDs of records with inactiveFlag as True
            inactive_ids = [item['id'] for item in data if item.get('inactiveFlag')]
            # Delete CompanyType records with inactiveFlag as True
            CompanyType.objects.filter(connectwise_config=connectwise_config, connectwise_manage_id__in=inactive_ids).delete()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while syncing CompanyTypes: {str(e)}"))

    def sync_company_statuses(self, connectwise_config, data):
        try:
            # Process and create/update CompanyStatus records
            for item in data:
                connectwise_manage_id = item.get('id')
                company_status_name = item.get('name')
                inactive_flag = item.get('inactive_flag')

                if not inactive_flag:
                    # Try to get an existing CompanyStatus record
                    company_status, created = CompanyStatus.objects.get_or_create(
                        connectwise_config=connectwise_config,
                        connectwise_manage_id=connectwise_manage_id,
                        defaults={'name': company_status_name}
                    )

                # Update the existing record if it already exists
                if not created:
                    company_status.name = company_status_name
                    company_status.save()

            # Remove any existing records not present in the ConnectWise response
            CompanyStatus.objects.filter(connectwise_config=connectwise_config).exclude(connectwise_manage_id__in=[item['id'] for item in data]).delete()
            # Extract IDs of records with inactiveFlag as True
            inactive_ids = [item['id'] for item in data if item.get('inactiveFlag')]
            # Delete CompanyType records with inactiveFlag as True
            CompanyStatus.objects.filter(connectwise_config=connectwise_config, connectwise_manage_id__in=inactive_ids).delete()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while syncing CompanyStatuses: {str(e)}"))

