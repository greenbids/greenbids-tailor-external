import contextlib
import datetime
from importlib.metadata import distribution
import logging
import os

from fastapi import FastAPI
from greenbids.tailor.core import telemetry, models
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from . import profiler, resources, tasks
from .routers import healthz, root

_logger = logging.getLogger(__name__)

@contextlib.asynccontextmanager
async def _lifespan(app: FastAPI):
    if resources.get_instance.cache_info().currsize > 0:
        _logger.warn("A resource object was initialized before app startup")
    resources.get_instance()
    with profiler.profile():
        yield


@tasks.repeat_every(
    seconds=float(
        os.environ.get(
            "GREENBIDS_TAILOR_MODEL_REFRESH_SECONDS",
        )
        or datetime.timedelta.max.total_seconds()
    ),
    wait_first=True,
    logger=_logger.getChild("model_reload"),
)
def _periodic_model_reload():
    model_name = os.environ.get("GREENBIDS_TAILOR_MODEL_NAME")
    if model_name is None:
        _logger.debug("Nothing to reload")
        return
    models.download(f"greenbids-tailor-models-{model_name}")
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
)

app.include_router(root.router)
app.include_router(healthz.router)
