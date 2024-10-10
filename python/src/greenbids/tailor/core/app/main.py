import contextlib
import logging
from importlib.metadata import distribution

from fastapi import FastAPI
from greenbids.tailor.core import models, telemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from . import profiler, resources, tasks
from .routers import healthz, ping, root

_logger = logging.getLogger(__name__)

@contextlib.asynccontextmanager
async def _lifespan(app: FastAPI):
    _setup_logging()
    if resources.get_instance.cache_info().currsize > 0:
        _logger.warning("A resource object was initialized before app startup")
    app_resources = resources.get_instance()
    tasks.repeat_every(
        seconds=app_resources.gb_model_refresh_period.total_seconds(),
        wait_first=True,
        logger=_logger.getChild("model_reload"),
    )(_periodic_model_reload)
    with profiler.profile():
        yield


def _setup_logging():
    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(logging.Formatter(fmt=logging.BASIC_FORMAT))

    logging.root.addHandler(stderr_handler)
    logging.root.addHandler(telemetry.handler)
    logging.getLogger("uvicorn.access").disabled = True


def _periodic_model_reload():
    app_resources = resources.get_instance()
    if app_resources.gb_model_name is str(None):
        _logger.debug("Nothing to reload")
        return
    models.download(f"greenbids-tailor-models-{app_resources.gb_model_name}")
    resources.get_instance().refresh_model()


pkg_dist = distribution("greenbids-tailor")
app = FastAPI(
    title=" ".join(pkg_dist.name.split("-")).title(),
    summary=str(pkg_dist.metadata.json.get("summary")),
    description=str(pkg_dist.metadata.json.get("description")),
    version=pkg_dist.version,
    lifespan=_lifespan,
)
FastAPIInstrumentor.instrument_app(
    app,
    tracer_provider=telemetry.tracer_provider,
    meter_provider=telemetry.meter_provider,
    excluded_urls=f"{healthz.router.prefix}/.*",
)

app.include_router(root.router)
app.include_router(healthz.router)
app.include_router(ping.router)
