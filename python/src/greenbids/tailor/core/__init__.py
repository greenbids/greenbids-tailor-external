import logging
import os

try:
    from ._version import version_tuple, version
except ImportError:
    version = "0.0.0"
    version_tuple = (0, 0, 0)

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())
LOGGER.setLevel(os.environ.get("GREENBIDS_TAILOR_LOG_LEVEL", "INFO").upper())

__all__ = ["version", "version_tuple", "LOGGER"]
