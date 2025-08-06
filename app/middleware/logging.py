import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from core.logging import get_contextual_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware pour logger toutes les requêtes HTTP."""

    def __init__(self, app, exclude_paths: set = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or {"/health", "/metrics"}

    async def dispatch(self, request: Request, call_next):
        # Skip logging pour certains endpoints
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        logger = get_contextual_logger("api.requests")
        start_time = time.perf_counter()

        # Logger la requête entrante (niveau DEBUG pour réduire le bruit)
        logger.debug(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": getattr(request.client, "host", "unknown"),
                "user_agent": request.headers.get("user-agent", "unknown")[
                    :100
                ],  # Limiter la taille
            },
        )

        try:
            response: Response = await call_next(request)
            process_time = (time.perf_counter() - start_time) * 1000

            # Logger selon le status code
            log_level = (
                "error"
                if response.status_code >= 500
                else "warning"
                if response.status_code >= 400
                else "info"
            )
            getattr(logger, log_level)(
                "Request completed",
                extra={
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time, 2),
                },
            )

            return response

        except Exception as e:
            process_time = (time.perf_counter() - start_time) * 1000
            logger.error(
                "Request failed",
                extra={
                    "error": str(e),
                    "error_type": e.__class__.__name__,
                    "process_time_ms": round(process_time, 2),
                },
                exc_info=True,
            )
            raise
