import uuid
import logging
from threading import local
from django.http import HttpResponse

_request_data = local()
logger = logging.getLogger('mappingUtility')

def get_request_id():
    return getattr(_request_data, 'request_id', None)

class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Assign a unique request ID
        request_id = str(uuid.uuid4())
        _request_data.request_id = request_id

        logger.info(f"Processing request {request.method} {request.path}", extra={'request_id': request_id})

        # Safely cache the request body
        try:
            request._body = request.body
        except Exception as e:
            logger.warning(f"[{request.path}] Could not cache request body: {e}", extra={'request_id': request_id})
            request._body = b''

        # Log Request
        try:
            if request.GET:
                logger.info(
                    f"Request {request.method} {request.path} | GET Params: {dict(request.GET)}",
                    extra={'request_id': request_id}
                )

            if request.FILES:
                logger.info(
                    f"Request {request.method} {request.path} | Uploaded Files: {[f.name for f in request.FILES.values()]}",
                    extra={'request_id': request_id}
                )

            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.content_type or ""
                if "multipart/form-data" in content_type:
                    # Log form-data fields
                    logger.info(
                        f"Request {request.method} {request.path} | Form Fields: {dict(request.POST)}",
                        extra={'request_id': request_id}
                    )
                else:
                    body = request._body.decode('utf-8', errors='replace')
                    logger.info(
                        f"Request {request.method} {request.path} | Body: {body}",
                        extra={'request_id': request_id}
                    )
        except Exception as e:
            logger.warning(f"[{request.path}] Failed to log request data: {e}", extra={'request_id': request_id})

        try:
            response = self.get_response(request)
        except Exception as e:
            logger.exception(f"[{request.path}] Unhandled exception: {e}", extra={'request_id': request_id})
            return HttpResponse("Internal Server Error", status=500)

        # Log Response
        try:
            content_type = response.get('Content-Type', '')
            if "application/octet-stream" not in content_type:
                response_body = response.content.decode('utf-8', errors='replace')
                logger.info(
                    f"Response {request.method} {request.path} | Status: {response.status_code} | Body: {response_body}",
                    extra={'request_id': request_id}
                )
            else:
                logger.info(
                    f"Response {request.method} {request.path} | Status: {response.status_code} | Binary Content",
                    extra={'request_id': request_id}
                )
        except Exception as e:
            logger.warning(f"[{request.path}] Could not log response body: {e}", extra={'request_id': request_id})

        return response
