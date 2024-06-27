import logging
import os

_logger = logging.getLogger("greenbids.tailor")
_logger.setLevel(os.environ.get("GREENBIDS_TAILOR_LOG_LEVEL", "INFO"))
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
_logger.handlers = [handler]
_logger.propagate = False
