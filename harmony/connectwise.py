from .utils import make_connectwise_api_call, log
from .models import ConnectWiseConfig, DataverseConfig, CompanyMapping, SyncMapping, ConnectWiseCompany, DataverseAccount
from .dataverse import get_dataverse_account, get_dataverse_contact
from datetime import datetime
import traceback

area = 'ConnectWise'

def create_connectwise_company(sync_mapping, dataverse_account_data):
    print('Not Implemented')

def get_connectwise_company():
    print('Not Implemented')

def get_connectwise_company_contacts(connectwise_company):
    print('Not Implemented')

def get_connectwise_contact(connectwise_contact=None, dataverse_contact=None, dataverse_contact_data=None, connectwise_config=None, sync_mapping=None, connectwise_contact_id=None):
    """
    Retrieve a ConnectWise Contact JSON object from ConnectWise Manage.  Look up by ConnectWiseContact record if known, the ConnectWise Contact ID, or search with information from a DataverseContact record, or Dataverse Contact JSON object.
    Returns the ConnectWise Contact JSON object with the respnse code.
    If a ConnectWiseContact record is not provided, then the SyncMapping object or ConnectWiseConfig object must be supploed.
    """
    try:
        response = None
        if sync_mapping:
            connectwise_config = sync_mapping.connectwise_config

        if connectwise_contact:
            connectwise_config = connectwise_contact.connectwise_company.connectwise_config
            connectwise_contact_id = connectwise_contact.connectwise_manage_id

        if connectwise_config and connectwise_contact_id:
            response, _ = make_connectwise_api_call(connectwise_config, f'company/contacts/{connectwise_contact_id}')

        if dataverse_contact and not connectwise_contact_id:
            dataverse_contact_data = get_dataverse_contact(dataverse_contact=dataverse_contact)

        if dataverse_contact_data and not connectwise_contact_id:
            if dataverse_contact_data.status_code == 200:
                dataverse_contact = parse_dataverse_contact_data(dataverse_contact_data)
                response = make_connectwise_api_call(connectwise_config, f'company/contacts?conditions=firstName={dataverse_contact["firstName"]} and lastName={dataverse_contact["lastName"]}')
            else:
                log('error', area, f'Unable to get a valid ConnectWise contact for a Dataverse contact.\n {response}')
        return response
    
    except Exception as e:
        message = f'An error occurred looking up a ConnectWise contact.\n{e}\n{traceback.format_exc()}'
        log('error', area, message)

def parse_dataverse_account_data(dataverse_account_data):
    account_data = {
        "name": dataverse_account_data.get("name", ""),
        "addressLine1": dataverse_account_data.get("address1_line1", ""),
        "addressLine2": dataverse_account_data.get("address1_line2", ""),
        "city": dataverse_account_data.get("address1_city", ""),
        "state": dataverse_account_data.get("address1_stateorprovince", ""),
        "zip": dataverse_account_data.get("address1_postalcode", ""),
        "country": [{"name": dataverse_account_data.get("address1_country", "")}],
        "phoneNumber": dataverse_account_data.get("telephone1", ""),
        "faxNumber": dataverse_account_data.get("address1_fax", ""),
        "website": dataverse_account_data.get("websiteurl", ""),
        "defaultContact": {"name": dataverse_account_data.get("address1_primarycontactname", "")},
    }
    return account_data

def parse_dataverse_contact_data(dataverse_contact_data):
    contact_data = {
        "firstName": dataverse_contact_data.get("firstname", ""),
        "lastName": dataverse_contact_data.get("lastname", ""),
        "addressLine1": dataverse_contact_data.get("address1_line1", ""),
        "addressLine2": dataverse_contact_data.get("address1_line2", ""),
        "city": dataverse_contact_data.get("address1_city", ""),
        "state": dataverse_contact_data.get("address1_stateorprovince", ""),
        "zip": dataverse_contact_data.get("address1_postalcode", ""),
        "country": {"name": dataverse_contact_data.get("address1_country", "")},
        "site": {"name": dataverse_contact_data.get("address1_name", "")},
        "department": {"name": dataverse_contact_data.get("department", "")},
        "title": dataverse_contact_data.get("jobtitle", ""),
    }
    communication_items = [
        {
            "defaultFlag": True,
            "value": dataverse_contact_data.get("emailaddress1", ""),
            "communicationType": "Email",
        },
        {
            "defaultFlag": True,
            "value": dataverse_contact_data.get("telephone1", ""),
            "communicationType": "Phone",
        },
    ]
    contact_data["communicationItems"] = communication_items
    return contact_data