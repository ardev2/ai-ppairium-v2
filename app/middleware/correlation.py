import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

# Context variables
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[str] = ContextVar("user_id", default="")


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware pour gérer les correlation IDs."""

    async def dispatch(self, request: Request, call_next):
        # Générer ou récupérer le correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request_id = str(uuid.uuid4())

        # Stocker dans le contexte
        correlation_id_var.set(correlation_id)
        request_id_var.set(request_id)
        request.state.correlation_id = correlation_id
        request.state.request_id = request_id

        # Récupérer user_id si présent (JWT, session, etc.)
        user_id = request.headers.get("X-User-ID", "")
        if user_id:
            user_id_var.set(user_id)

        # Traiter la requête
        response = await call_next(request)

        # Ajouter les IDs à la réponse
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Request-ID"] = request_id

        return response
