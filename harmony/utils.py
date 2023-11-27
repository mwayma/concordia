import requests
import base64
import msal
from django.conf import settings
from django.core.cache import cache
from datetime import timedelta
from .models import Log, LogType

def log(type='debug', area=None, message=None):
    # Check if this is a log about logging
    if type.lower() == 'debug' and area == 'Log' and message.startswith('Log'):
        return
    
    log_type = LogType.objects.get(name__iexact=type)
    if log_type.id < settings.LOGGING_LEVEL:
        return
    
    if log_type:
        log = Log.objects.create(
            type = log_type,
            area = area,
            message = message
        )
        log.save()
    else:
        log(type='error', area='System', message=f'Unable to log a message due to lack of correct log_type.  The message was: {message}')

def get_url(connectwise_config, endpoint):
    # Use the ConnectWiseConfig ID as part of the cache key
    codebase_cache_key = f'codebase_version_{connectwise_config.pk}'
    isCloud_cache_key = f'isCloud_{connectwise_config.pk}'

    # Try to get the codebase version and cloud status from the cache
    codebase_version = cache.get(codebase_cache_key)
    isCloud = cache.get(isCloud_cache_key)

    if codebase_version or isCloud is None:
        # If not found in the cache, make the request to the Company Info endpoint
        company_info_url = f'{connectwise_config.base_url}/login/companyinfo/{connectwise_config.company_id}'
        response = requests.get(company_info_url)
        company_info = response.json()
        codebase_version = company_info.get("Codebase", "v4_6_release")
        isCloud = company_info.get("IsCloud", False)

        # Cache the codebase version with an expiration time (e.g., 1 day)
        cache.set(codebase_cache_key, codebase_version, timeout=timedelta(days=1).total_seconds())
        cache.set(isCloud_cache_key, isCloud, timeout=timedelta(days=1).total_seconds())

    api_url = f'{connectwise_config.base_url}/{codebase_version}apis/3.0/{endpoint}'
    if isCloud:
        api_url = f'api-{api_url}'
        
    return api_url

def get_connectwise_headers(connectwise_config):
    credentials = f"{connectwise_config.company_id}+{connectwise_config.api_public_key}:{connectwise_config.api_private_key}"
    credentials_base64 = base64.b64encode(credentials.encode()).decode()
    headers = {
        'Authorization': f'Basic {credentials_base64}',
        'Content-Type': 'application/json',
        'clientId': settings.CONNECTWISE_CLIENT_ID,
    }
    return headers

def extract_next_page_url(link_header):
    parts = link_header.split('; ')
    for part in parts:
        if 'rel="next"' in part:
            return part.strip('<>')

    return None

def make_connectwise_api_call(connectwise_config, endpoint, method='get', params=None, data=None):
    api_url = get_url(connectwise_config, endpoint)
    headers = get_connectwise_headers(connectwise_config)
    params = params or {}
    data = data or {}

    # Use the requests library's request function with the specified method
    response = requests.request(method, api_url, params=params, json=data, headers=headers)

    # Check if there are pagination headers
    next_page_url = extract_next_page_url(response.headers.get('link', ''))

    # Return both response_data and next_page_url
    response_data = response.json()
    return response_data, next_page_url

def getMsalToken(dataverse_config):
    tenant_id = dataverse_config.tenant_id
    client_id = dataverse_config.client_id
    client_secret = dataverse_config.client_secret
    authority = f'https://login.microsoftonline.com/{tenant_id}'

    # Create a ConfidentialClientApplication
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=client_secret
    )

    # Acquire a token
    result = app.acquire_token_for_client(scopes=[f'{dataverse_config.environment_url}/.default'])
    if 'expires_in' in result:
        # Store the token along with its expiration time in the cache
        cache.set(f'{dataverse_config.pk}_access_token', result['access_token'], timeout=result['expires_in'])
    return result['access_token']

def make_dataverse_api_call(dataverse_config, endpoint, method='get', headers=None, params=None, data=None):
    params = params or {}
    data = data or {}
    access_token = cache.get(f'{dataverse_config.pk}_access_token')
    if not access_token:
        access_token = getMsalToken(dataverse_config)

    http_headers = {'Authorization': 'Bearer ' + access_token,
                'Accept': 'application/json',
                'Content-Type': 'application/json'}
    api_url = f'{dataverse_config.environment_url}/api/data/v9.2/{endpoint}'
    if headers:
        http_headers.update(headers)
    response = requests.request(method, api_url, headers=http_headers, params=params, json=data, stream=False)
    return response