import logging
import sys
import os

from app.core.config import settings


def setup_logger(name: str = "TextHelper"):
    """
    Setup centralized logging configuration.
    Respects LOG_LEVEL from settings.
    """
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # Avoid duplicate handlers when re-imported
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file logging (can be enabled via env or later)
    # log_dir = os.getenv("LOG_DIR")
    # if log_dir:
    #     os.makedirs(log_dir, exist_ok=True)
    #     file_handler = logging.FileHandler(
    #         os.path.join(log_dir, "texthelper.log"), encoding="utf-8"
    #     )
    #     file_handler.setFormatter(formatter)
    #     logger.addHandler(file_handler)

    return logger


logger = setup_logger()
