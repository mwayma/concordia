import requests
import base64
from django.conf import settings

def get_connectwise_headers(connectwise_config):
    credentials = f"{connectwise_config.company_id}+{connectwise_config.api_public_key}:{connectwise_config.api_private_key}"
    credentials_base64 = base64.b64encode(credentials.encode()).decode()
    headers = {
        'Authorization': f'Basic {credentials_base64}',
        'Content-Type': 'application/json',
        'clientId': settings.CONNECTWISE_CLIENT_ID,
    }
    return headers

def make_connectwise_api_call(connectwise_config, endpoint, method='get', data=None):
    api_url = f'{connectwise_config.base_url}/v4_6_release/apis/3.0/{endpoint}'
    headers = get_connectwise_headers(connectwise_config)
    data = data or {}

    # Use the requests library's request function with the specified method
    response = requests.request(method, api_url, json=data, headers=headers)
                                
    return response.json()