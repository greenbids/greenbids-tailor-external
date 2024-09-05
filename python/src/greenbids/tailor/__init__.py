import logging
import os

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())
LOGGER.setLevel(os.environ.get("GREENBIDS_TAILOR_LOG_LEVEL", "INFO"))
