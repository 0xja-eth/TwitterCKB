# ./config/logging_config.py
import logging
from logging.handlers import TimedRotatingFileHandler
import os

# Ensure the logs directory exists
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Logging configuration
LOG_FILE = os.path.join(LOG_DIR, "app.log")

logging.basicConfig(
    level=logging.INFO,  # Default log level
    format="%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to console
        TimedRotatingFileHandler(LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8"),  # Log to file, rotated daily
    ],
)

# Create a logger instance for the app
logger = logging.getLogger("fastapi_app")


