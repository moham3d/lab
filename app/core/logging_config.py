"""
Logging configuration for production
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration for different environments"""

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(client_ip)s - %(method)s - %(url)s - %(status_code)s - %(process_time)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z"
            },
            "simple": {
                "format": "[%(levelname)s] %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "simple",
                "stream": sys.stdout
            }
        },
        "loggers": {
            "app": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "app.security": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "app.api": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            }
        },
                "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }

    return config


def setup_logging():
    """Setup logging configuration"""
    config = get_logging_config()
    logging.config.dictConfig(config)

    # Set up specific loggers
    logger = logging.getLogger("app")
    logger.info("Logging system initialized")

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(f"app.{name}")


# Global logger instance
logger = setup_logging()