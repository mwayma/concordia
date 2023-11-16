from django.core.management.base import BaseCommand
from harmony.models import ConnectWiseConfig
from harmony.utils import make_connectwise_api_call

class Command(BaseCommand):
    help = 'Fetch ConnectWise boards for all configurations'

    def handle(self, *args, **kwargs):
        # Fetch all ConnectWiseConfig instances
        connectwise_configs = ConnectWiseConfig.objects.all()

        if connectwise_configs:
            for connectwise_config in connectwise_configs:
                data = make_connectwise_api_call(connectwise_config, 'service/boards', method='get')
                # Process the data or handle errors as needed
                self.stdout.write(self.style.SUCCESS(f"Boards for {connectwise_config.company_name}: {data}"))
        else:
            self.stdout.write(self.style.WARNING("No ConnectWiseConfig instances found. Please configure one or more."))