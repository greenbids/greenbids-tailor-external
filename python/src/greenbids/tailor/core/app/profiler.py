import contextlib
import logging
import os

_logger = logging.getLogger(__name__)


@contextlib.contextmanager
def profile():
    if os.environ.get("GREENBIDS_TAILOR_PROFILE"):
        import cProfile

        _logger.info("Profiling enabled")
        profiler = cProfile.Profile()
        profiler.enable()
    else:
        profiler = None

    yield

    if profiler:
        _logger.info("Dumping profile...")
        profiler.dump_stats(str(os.environ["GREENBIDS_TAILOR_PROFILE"]))
