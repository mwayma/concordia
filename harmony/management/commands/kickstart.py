from django.core.management.base import BaseCommand
from harmony.tasks import import_company_data_task, import_companies_task
from datetime import timedelta

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        import_company_data_task(repeat=86400, repeat_until=None)
        import_companies_task(repeat=86400, repeat_until=None)