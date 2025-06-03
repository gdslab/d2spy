try:
    from importlib.metadata import version, PackageNotFoundError

    __version__ = version("d2spy")
except PackageNotFoundError:
    __version__ = "unknown"

from d2spy.utils.logging_config import setup_logging

# Initialize logging with default settings
setup_logging()
