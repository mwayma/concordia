from .utils import log
import traceback

class ExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            exception_str = traceback.format_exc()
            log(type='error', area='System', message=f'Unhandled exception: {e}\r\n{exception_str}')
            raise

        return response