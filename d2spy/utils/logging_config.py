import logging
import sys
from typing import Optional


def setup_logging(level: Optional[int] = None) -> None:
    """Configure logging for the d2spy package.

    Args:
        level (Optional[int]): The logging level to use. If None, defaults to INFO.
    """
    # Get the root logger
    logger = logging.getLogger("d2spy")

    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Create formatter
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Set level (default to INFO if not specified)
    logger.setLevel(level or logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module.

    Args:
        name (str): The name of the module requesting the logger.

    Returns:
        logging.Logger: A logger instance configured for the module.
    """
    return logging.getLogger(f"d2spy.{name}")
