from .utils import make_dataverse_api_call
from .models import ConnectWiseConfig, DataverseConfig, CompanyMapping, SyncMapping, ConnectWiseCompany, DataverseAccount
from datetime import datetime

def create_dataverse_account(sync_mapping, connectwise_company_data):
    try:
        # Map ConnectWise data to Dataverse structure
        account_data = {
            "name": connectwise_company_data[0]["name"],
            "address1_line1": connectwise_company_data[0].get("addressLine1",""),
            "address1_line2": connectwise_company_data[0].get("addressLine2",""),
            "address1_city": connectwise_company_data[0].get("city",""),
            "address1_stateorprovince": connectwise_company_data[0].get("state", ""),
            "address1_postalcode": connectwise_company_data[0].get("zip",""),
            "address1_country": connectwise_company_data[0].get("country", [{}])[0].get("name", ""),
            "telephone1": connectwise_company_data[0].get("phoneNumber",""),
            "websiteurl": connectwise_company_data[0].get("website","")
        }

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

            # Create the new DataverseAccount rebord
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
            # Print or log the created accountid
            print(f"Dynamics 365 accountid: {accountid}")
        else:
            print(f"Error creating account {connectwise_company_data[0]['name']}: {response}")
            
    except Exception as e:
        print(f"{str(e)}")
