import logging
import sys
from datetime import datetime
from typing import Dict, Any
from pythonjsonlogger import jsonlogger
from middleware.correlation import correlation_id_var, request_id_var, user_id_var
from config.settings import settings


class EnhancedJSONFormatter(jsonlogger.JsonFormatter):
    """Formatteur JSON avec injection automatique du contexte."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ):
        super().add_fields(log_record, record, message_dict)

        # Métadonnées de base
        log_record.update(
            {
                "@timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname.lower(),
                "logger": record.name,
                "service": settings.APP_NAME,
                "environment": settings.ENVIRONMENT,
            }
        )

        # Injection automatique du contexte depuis ContextVar
        if correlation_id := correlation_id_var.get(""):
            log_record["correlation_id"] = correlation_id
        if request_id := request_id_var.get(""):
            log_record["request_id"] = request_id
        if user_id := user_id_var.get(""):
            log_record["user_id"] = user_id

        # Nettoyer les champs sensibles
        self._sanitize_sensitive_fields(log_record)

    def _sanitize_sensitive_fields(self, log_record: Dict[str, Any]):
        """Masque les données sensibles."""
        sensitive_keys = {"password", "token", "authorization", "secret", "api_key"}

        for key, value in list(log_record.items()):
            if key.lower() in sensitive_keys:
                log_record[key] = "***REDACTED***"
            elif isinstance(value, dict):
                self._sanitize_dict(value, sensitive_keys)

    def _sanitize_dict(self, d: dict, sensitive_keys: set):
        for key, value in list(d.items()):
            if key.lower() in sensitive_keys:
                d[key] = "***REDACTED***"
            elif isinstance(value, dict):
                self._sanitize_dict(value, sensitive_keys)


class ContextualLoggerAdapter(logging.LoggerAdapter):
    """Adaptateur qui injecte automatiquement le contexte."""

    def process(self, msg, kwargs):
        # Le contexte sera injecté par le formatter, pas besoin de le faire ici
        return msg, kwargs


def setup_logging():
    """Configure le système de logging de manière optimisée."""

    # Désactiver les loggers bruyants
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Configuration du formatter
    if settings.LOG_FORMAT.lower() == "json":
        formatter = EnhancedJSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s (req_id=%(request_id)s)",
            datefmt="%H:%M:%S",
        )

    # Handler principal
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    root_logger.addHandler(handler)

    # Éviter la duplication des logs
    root_logger.propagate = False


def get_contextual_logger(name: str) -> ContextualLoggerAdapter:
    """Factory pour créer des loggers contextuels."""
    base_logger = logging.getLogger(name)
    return ContextualLoggerAdapter(base_logger, {})


# Logger par défaut
logger = get_contextual_logger(__name__)

# Initialiser au import
setup_logging()
