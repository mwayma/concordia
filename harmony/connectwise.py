from .utils import make_connectwise_api_call
from .models import ConnectWiseConfig, DataverseConfig, CompanyMapping, SyncMapping, ConnectWiseCompany, DataverseAccount
from datetime import datetime

def create_connectwise_company(sync_mapping, dataverse_account_data):
    print('Not Implemented')

def get_connectwise_company():
    print('Not Implemented')

def get_connectwise_contact(connectwise_config, contact_id):
    contact, _ = make_connectwise_api_call(connectwise_config, f'company/contacts/{contact_id}')
    return contact