import logging.config
import logging.config
from logging import Filter
from typing import Dict, Union, Type

from pydantic import BaseModel

from Middleware.custom_middleware import SourceFilter, IPMACFilter
from Utils.V1.utility_functions import utility


class LogConfig(BaseModel):
    LOGGER_NAME: str = "DRIVE_SHARING_LOGGER"  # name
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s| %(correlation_id)s  | %(ip_address)s | %(mac_address)s | %(source)s | %(user_id)s | %(funcName)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE_MAX_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB

    LOG_FILE_PATH: str = utility.get_path(
        utility.get_ini_path('PATH', 'LOGGER_PATH', True),
        file_name=f"drive_sharing.log")  # name

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    filters: Dict[str, Dict[str, Union[str, int, Type[Filter]]]] = {
        'correlation_id': {
            '()': 'asgi_correlation_id.CorrelationIdFilter',
            'uuid_length': 32,
            'default_value': '-',
        },
        'source_filter': {
            '()': SourceFilter,
            'default_source': '-'
        },
        'ip_mac_filter': {
            '()': IPMACFilter,
            'default_source': '-'
        }
    }
    formatters: Dict[str, Dict[str, str]] = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: Dict[str, Dict[str, object]] = {
        "default": {
            "formatter": "default",
            'filters': ['correlation_id', 'source_filter', 'ip_mac_filter'],
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "TimedRotatingFileHandler": {
            "formatter": "default",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOG_FILE_PATH,  # Specify the file name for logs
            "when": 'midnight',
            "backupCount": 0,
        }
    }

    loggers: Dict[str, Dict[str, object]] = {
        LOGGER_NAME: {"handlers": ["default", "TimedRotatingFileHandler"], "level": LOG_LEVEL},
    }


logging.config.dictConfig(LogConfig().model_dump())

logger = logging.getLogger('DRIVE_SHARING_LOGGER')  # name
