def log_api_request(logger, request, message, level="info"):
    log_method = getattr(logger, level, logger.info)
    log_method(
        message,
        extra={
            "method": request.method,
            "path": request.path,
            # 'user': getattr(request.user, 'id', None)
        },
    )
