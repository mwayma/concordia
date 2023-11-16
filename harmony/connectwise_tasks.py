import threading
from .models import ConnectWiseConfig
from .utils import make_connectwise_api_call

def get_company_status(connectwise_config):
    data = make_connectwise_api_call(connectwise_config, 'company/companies/statuses', method='get')
    # Process the data or handle errors as needed
    print(f"Company Statuses for {connectwise_config.company_name}: {data}")

def get_company_types(connectwise_config):
    data = make_connectwise_api_call(connectwise_config, 'company/companies/types', method='get')
    # Process the data or handle errors as needed
    print(f"Company Types for {connectwise_config.company_name}: {data}")

def get_boards(connectwise_config):
    data = make_connectwise_api_call(connectwise_config, 'service/boards', method='get')
    # Process the data or handle errors as needed
    print(f"Boards for {connectwise_config.company_name}: {data}")

def iterate_connectwise_configs():
    # Retrieve all ConnectWiseConfig instances
    connectwise_configs = ConnectWiseConfig.objects.all()

    # Start a thread for each ConnectWiseConfig instance
    threads = []
    for config in connectwise_configs:
        thread = threading.Thread(target=get_boards, args=(config,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()