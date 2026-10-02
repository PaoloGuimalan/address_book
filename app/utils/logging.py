import os
import logging
import sys

LOG_DIR = "logs"


def setup_logging():
    """Initializes the base directory and basic console output for the server."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    log_format = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if root_logger.handlers:
        root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)


def get_module_logger(name: str) -> logging.Logger:
    """
    Dynamically creates or retrieves a logger that automatically writes
    to a file matching the provided 'name' inside the /logs directory.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = True

    if not any(isinstance(h, logging.FileHandler) for h in logger.handlers):
        log_format = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s (Line %(lineno)d): %(message)s"
        )

        os.makedirs(LOG_DIR, exist_ok=True)
        log_file_path = os.path.join(LOG_DIR, f"{name}.log")

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(log_format)
        file_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)

    return logger
