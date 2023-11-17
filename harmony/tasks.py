from background_task import background
from django.core.management import call_command
from django.core.cache import cache
from datetime import timedelta, datetime

@background(remove_existing_tasks=True)
def import_company_data_task():
    last_ran = cache.get('import_company_data_timestamp')

    if last_ran is None or (datetime.now() - last_ran) > timedelta(hours=24):
        call_command('import_company_data')
        cache.set('import_company_data_timestamp', datetime.now())

@background(remove_existing_tasks=True)
def import_companies_task():
    last_ran = cache.get('import_companies_timestamp')

    if last_ran is None or (datetime.now() - last_ran) > timedelta(hours=24):
        call_command('import_companies')
        cache.set('import_companies_timestamp', datetime.now())