import contextlib
from importlib.metadata import distribution

from fastapi import FastAPI

from greenbids.tailor.core import telemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from . import resources, profiler
from .routers import root, healthz


@contextlib.asynccontextmanager
async def _lifespan(app: FastAPI):
    resources.APP_RESOURCES.setup()
    with profiler.profile():
        yield


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
