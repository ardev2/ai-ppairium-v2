import logging
import sys
from datetime import datetime
from typing import Dict, Any
from pythonjsonlogger import jsonlogger
from config.settings import settings


class CustomJSONFormatter(jsonlogger.JsonFormatter):
    """Formatteur JSON personnalisé avec métadonnées."""

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ):
        super().add_fields(log_record, record, message_dict)

        # Ajouter des métadonnées personnalisées
        log_record["timestamp"] = datetime.now().isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["service"] = settings.APP_NAME
        log_record["version"] = settings.APP_VERSION
        log_record["environment"] = settings.ENVIRONMENT

        # Ajouter des informations de contexte si disponibles
        if hasattr(record, "user_id"):
            log_record["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        if hasattr(record, "correlation_id"):
            log_record["correlation_id"] = record.correlation_id


def setup_logging():
    """Configure le système de logging."""

    if settings.LOG_FORMAT.lower() == "json":
        formatter = CustomJSONFormatter(
            fmt="%(timestamp)s %(level)s %(name)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Configuration du handler principal
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    root_logger.addHandler(handler)

    # Configuration spécifique pour certains loggers
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Logger pour les requêtes HTTP personnalisées
    request_logger = logging.getLogger("api.requests")
    request_logger.setLevel(logging.INFO)


class ContextualLogger:
    """Logger avec contexte pour tracer les requêtes."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def with_context(self, **context):
        """Retourne un logger avec contexte."""
        return ContextualLoggerAdapter(self.logger, context)


class ContextualLoggerAdapter(logging.LoggerAdapter):
    """Adaptateur de logger qui ajoute du contexte."""

    def process(self, msg, kwargs):
        # Ajouter le contexte aux extra
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        kwargs["extra"].update(self.extra)
        return msg, kwargs


# Initialiser le logging
setup_logging()

# Logger par défaut pour l'application
logger = ContextualLogger(__name__)
