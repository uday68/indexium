import logging
from app.core.observability.logging import configure_logging


def setup_app_logging():
    configure_logging(level="INFO", json_format=False)
