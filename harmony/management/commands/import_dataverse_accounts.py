from django.core.management.base import BaseCommand
from harmony.models import DataverseConfig
from harmony.utils import make_dataverse_api_call

class Command(BaseCommand):
    help = 'Import accounts from Dataverse'

    def handle(self, *args, **kwargs):
        dataverse_configs = DataverseConfig.objects.all()
        for dataverse_config in dataverse_configs:
            make_dataverse_api_call(dataverse_config, endpoint=None)