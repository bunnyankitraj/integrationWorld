import uuid
from threading import local

_request_data = local()

def get_request_id():
    return getattr(_request_data, 'request_id', None)

class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _request_data.request_id = str(uuid.uuid4())
        response = self.get_response(request)
        return response
