"""
Logging configuration for Insurance Analytics Platform
"""

import logging
import logging.handlers
from pathlib import Path
from config.settings import LOG_LEVEL, LOG_FILE

# Ensure log directory exists
log_file_path = Path(LOG_FILE)
log_file_path.parent.mkdir(parents=True, exist_ok=True)

# Create logger
logger = logging.getLogger("insurance_analytics")
logger.setLevel(getattr(logging, LOG_LEVEL))

# Create formatters
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# File handler with rotation
file_handler = logging.handlers.RotatingFileHandler(
    LOG_FILE,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(f"insurance_analytics.{name}")

__all__ = ["logger", "get_logger"]
