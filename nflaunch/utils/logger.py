"""Logging configuration for nflaunch."""

import logging
import os


def set_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger with nflaunch's standard formatting.

    Args:
        name: Logger name, typically the class or module requesting logging.

    Returns:
        A logger instance with console handler and environment-driven log level.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Reuse existing handler configuration
        return logger

    level_name = os.getenv("NF_LAUNCH_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
