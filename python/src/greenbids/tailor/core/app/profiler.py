import contextlib
import logging
from . import resources

_logger = logging.getLogger(__name__)


@contextlib.contextmanager
def profile():
    profiling_output = resources.get_instance().profiling_output
    if profiling_output:
        import cProfile

        _logger.info("Profiling enabled")
        profiler = cProfile.Profile()
        profiler.enable()
    else:
        profiler = None

    yield

    if profiler:
        _logger.info("Dumping profile...")
        profiler.dump_stats(profiling_output)
