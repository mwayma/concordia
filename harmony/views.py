import json
from django.http import JsonResponse
from .utils import make_connectwise_api_call
from .models import ConnectWiseConfig

def fetch_connectwise_boards(request):
    # Fetch all ConnectWiseConfig instances
    connectwise_configs = ConnectWiseConfig.objects.all()

    if connectwise_configs:
        response_data = {}
        for connectwise_config in connectwise_configs:
            data = make_connectwise_api_call(connectwise_config, 'service/boards', method='get')
            # Process the data or handle errors as needed
            print(f"Boards for {connectwise_config.company_id}: {data}")
            response_data[connectwise_config.company_id] = data

        return JsonResponse(response_data, safe=False)
    else:
        return JsonResponse({'error': 'No ConnectWiseConfig instances found. Please configure one or more.'})