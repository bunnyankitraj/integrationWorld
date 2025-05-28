import logging

from mappingProject.middleware import get_request_id


class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id() or None

        # These fields can be set by views using logger with `extra=`
        record.method = getattr(record, "method", None)
        record.path = getattr(record, "path", None)
        return True


class ConditionalFormatter(logging.Formatter):
    def format(self, record):
        base_message = super().format(record)
        extras = []

        if getattr(record, "request_id", None):
            extras.append(f"[request_id={record.request_id}]")
        if getattr(record, "method", None):
            extras.append(f"[method={record.method}]")
        if getattr(record, "path", None):
            extras.append(f"[path={record.path}]")

        return f"{base_message} {' '.join(extras)}"
