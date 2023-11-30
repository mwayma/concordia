from .utils import make_dataverse_api_call, log
from .models import CompanyMapping, ConnectWiseCompany, DataverseAccount, ConnectWiseContact, DataverseContact, ContactMapping
from .connectwise import get_connectwise_contact
import traceback

area = 'Dataverse'

def create_dataverse_account(sync_mapping, connectwise_company_data):
    try:
        # Map ConnectWise data to Dataverse structure
        account_data = parse_connectwise_company_data(connectwise_company_data)

        headers = {"Prefer": "return=representation"} 
        connectwise_manage_id = connectwise_company_data[0]["id"]
        dataverse_config = sync_mapping.dataverse_config
        connectwise_config = sync_mapping.connectwise_config
        connectwise_company = ConnectWiseCompany.objects.get(
            connectwise_config=connectwise_config,
            connectwise_manage_id=connectwise_manage_id
        )
        response = make_dataverse_api_call(dataverse_config, 'accounts', method='post', headers=headers, data=account_data)

        if response.status_code == 201:
            # Parse the response JSON to get the created accountid
            created_data = response.json()
            accountid = created_data.get("accountid")

            # Create the new DataverseAccount record
            dataverse_account = DataverseAccount.objects.create(
                dataverse_config = dataverse_config,
                dataverse_id = accountid,
                dataverse_name = connectwise_company_data[0]["name"]
            )
            dataverse_account.save()

            # Create the mapping between the two company records

            company_mapping = CompanyMapping.objects.create(
                sync_mapping = sync_mapping,
                connectwise_company = connectwise_company,
                dataverse_account = dataverse_account
            )
            company_mapping.save()
            log(type='info', area=area, message=f"Created Dataverse account {dataverse_config.environment_url}: {dataverse_account.dataverse_name}")

            if connectwise_company_data[0].get("defaultContact"):
                connectwise_contact_id = connectwise_company_data[0].get("defaultContact", {}).get("id")
                # Get the actual contact object from ConnectWise as the embedded object does not have all the info we need.
                contact = get_connectwise_contact(connectwise_config, connectwise_contact_id)
                contact_data = parse_connectwise_contact_data(contact)

                #Extra for being the primary
                extra_contact_data = {
                    "parentcustomerid_account@odata.bind": f"/accounts({accountid})",
                }
                contact_data.update(extra_contact_data)

                connectwise_contact, created = ConnectWiseContact.objects.get_or_create(
                    connectwise_company = connectwise_company,
                    connectwise_manage_id = connectwise_contact_id
                )
                if not created and (connectwise_contact.first_name != contact.get("firstName") or connectwise_contact.last_name != contact.get("lastName")):
                    # Update the contact's first and last names
                    connectwise_contact.first_name = contact.get("firstName")
                    connectwise_contact.last_name = contact.get("lastName")
                    connectwise_contact.save()

                connectwise_company.primary_contact = connectwise_contact
                connectwise_company.save()

                contact_response = make_dataverse_api_call(dataverse_config, 'contacts', method='post', headers=headers, data=contact_data)
                dataverse_contact = None
                if contact_response.status_code == 201:
                    contact_created_data = contact_response.json()
                    dataverse_contact = DataverseContact.objects.create(
                        dataverse_account = dataverse_account,
                        dataverse_id = contact_created_data.get('contactid'),
                        first_name = connectwise_contact.first_name,
                        last_name = connectwise_contact.last_name
                    )
                    dataverse_contact.save()

                    dataverse_account.primary_contact = dataverse_contact
                    dataverse_account.save()

                    contact_mapping = ContactMapping.objects.create(
                        sync_mapping = sync_mapping,
                        connectwise_contact = connectwise_contact,
                        dataverse_contact = dataverse_contact
                    )
                    contact_mapping.save()
                else:
                    log(type='error', area=area, message=f"Error creating Dataverse contact {dataverse_config.environment_url}: {connectwise_contact.first_name} {connectwise_contact.last_name}.  Did not receive expected response\n: {contact_response} \n {contact_response.json()}")

                # Come back and attach the new Dataverse contact as the default contact for the account
                if dataverse_contact:
                    patch_data = {
                        "primarycontactid@odata.bind": f"/contacts({dataverse_contact.dataverse_id})"
                    }
                    contact_patch_response = make_dataverse_api_call(dataverse_config, f'accounts({dataverse_account.dataverse_id})', 'patch', data=patch_data)
                    if contact_patch_response.status_code != 204:
                        log('error', area, f'Unable to update dataverse account primary contact.  Account: {dataverse_account.dataverse_name}. Contact: {dataverse_contact.first_name} {dataverse_contact.last_name}. Did not receive an expected response.\n{response}')                
        else:
            log(type="error", area=area, message=f"Error creating Dataverse account {dataverse_config.environment_url}: {dataverse_account.dataverse_name}.  Did not receive expected response\n: {response}")
            
    except Exception as e:
        message = f'An error occurred while creating a Dataverse account: {connectwise_company_data[0]["name"]}\n{e}\n{traceback.format_exc()}'
        log('error', area, message)
        print(f'error: {message}')

def edit_dataverse_account(dataverse_account, connectwise_company_data=None, delete=False):
    try:
        account_data = None
        if connectwise_company_data:
            account_data = parse_connectwise_company_data(connectwise_company_data)
        method = 'patch'
        if delete:
            method = 'delete'
            
        dataverse_config = dataverse_account.dataverse_config
        response = make_dataverse_api_call(dataverse_config, f'accounts({dataverse_account.dataverse_id})', method=method, data=account_data)

        if response.status_code == 204:
            action = 'Edit'
            if delete:
                action = 'Delete'
            log(type='info', area=area, message=f"Performing {action} Dataverse account {dataverse_config.environment_url}: {dataverse_account.dataverse_name}")
        else:
            log(type="error", area=area, message=f"Error performing {action} on Dataverse account {dataverse_config.environment_url}: {dataverse_account.dataverse_name}.  Did not receive expected response\n: {response} \n {response.json()}")
            
    except Exception as e:
        message = f'An error occurred while editing a Dataverse account. {dataverse_account.dataverse_name}: {connectwise_company_data}\n{e}\n{traceback.format_exc()}'
        log('error', area, message)

def edit_dataverse_contact(dataverse_contact, connectwise_contact_data=None, delete=False):
    try:
        contact_data = None
        if connectwise_contact_data:
            contact_data = parse_connectwise_company_data(connectwise_contact_data)
        method = 'patch'
        if delete:
            method = 'delete'
        dataverse_config = dataverse_contact.dataverse_config
        response = make_dataverse_api_call(dataverse_config, f'contacts({dataverse_contact.dataverse_id})', method=method, data=contact_data)

        action = 'Edit'
        if delete:
            action = 'Delete'
        if response.status_code == 204:
            log(type='info', area=area, message=f"Performed {action} on Dataverse contact {dataverse_config.first_name} {dataverse_contact.last_name}")
        else:
            log(type="error", area=area, message=f"Error performing {action} on Dataverse contact {dataverse_config.first_name} {dataverse_contact.last_name}.  Did not receive expected response\n: {response}\n {response.json()}")
            
    except Exception as e:
        message = f'An error occurred while editing a Dataverse contact. {dataverse_contact.first_name} {dataverse_contact.last_name}: {connectwise_contact_data}\n{e}\n{traceback.format_exc()}'
        log('error', area, message)

def parse_connectwise_company_data(connectwise_company_data):
    account_data = {
        "name": connectwise_company_data[0]["name"],
        "address1_line1": connectwise_company_data[0].get("addressLine1",""),
        "address1_line2": connectwise_company_data[0].get("addressLine2",""),
        "address1_city": connectwise_company_data[0].get("city",""),
        "address1_stateorprovince": connectwise_company_data[0].get("state", ""),
        "address1_postalcode": connectwise_company_data[0].get("zip",""),
        "address1_country": connectwise_company_data[0].get("country", [{}])[0].get("name", ""),
        "telephone1": connectwise_company_data[0].get("phoneNumber",""),
        "address1_fax": connectwise_company_data[0].get("faxNumber",""),
        "websiteurl": connectwise_company_data[0].get("website",""),
        "address1_primarycontactname": connectwise_company_data[0].get("defaultContact", {}).get("name", "")
    }
    return account_data

def parse_connectwise_contact_data(contact):
    contact_data = {
        "firstname": contact.get("firstName", ""),
        "lastname": contact.get("lastName", ""),
        "telephone1": get_primary_phone(contact),
        "address1_name": contact.get('site', {}).get('name'),
        "address1_line1": contact.get("addressLine1", ""),
        "address1_line2": contact.get("addressLine2", ""),
        "address1_city": contact.get("city", ""),
        "address1_stateorprovince": contact.get("state", ""),
        "address1_postalcode": contact.get("zip", ""),
        "address1_country": contact.get("country", {}).get("name", ""),
        "department": contact.get("department", {}).get("name", ""),
        "emailaddress1": get_primary_email(contact),
        "jobtitle": contact.get("title", ""),
    }
    return contact_data

def get_primary_email(connectwise_contact_data):
    # Check if communicationItems array exists
    if 'communicationItems' in connectwise_contact_data:
        # Iterate through communicationItems
        for item in connectwise_contact_data['communicationItems']:
            # Check if the item is a primary email and is of type 'Email'
            if item.get('defaultFlag') and item.get('communicationType') == 'Email':
                return item.get('value')

    # Return None if primary email is not found
    return None

def get_primary_phone(connectwise_contact_data):
    # Check if communicationItems array exists
    if 'communicationItems' in connectwise_contact_data:
        # Iterate through communicationItems
        for item in connectwise_contact_data['communicationItems']:
            # Check if the item is a primary phone number and is of type 'Phone'
            if item.get('defaultFlag') and item.get('communicationType') == 'Phone':
                return item.get('value')

    # Return None if primary phone number is not found
    return None
