import contextlib
import dataclasses
import logging
import math
import os
import time
from importlib.metadata import distribution

import pydantic
from fastapi import FastAPI, HTTPException, status
from greenbids.tailor.core import fabric, models, telemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

_logger = logging.getLogger(__name__)


@dataclasses.dataclass
class AppResources:
    model: models.Model = models.NullModel()
    start_monotonic: float = math.nan

    class _Healthz(pydantic.BaseModel):
        model: str
        uptime: float

    @property
    def healthz(self) -> _Healthz:
        return self._Healthz(
            model=self.model.__class__.__qualname__,
            uptime=time.monotonic() - self.start_monotonic,
        )


APP_RESOURCES = AppResources()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    APP_RESOURCES.model = models.get_model()
    APP_RESOURCES.start_monotonic = time.monotonic()
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


pkg_dist = distribution("greenbids-tailor")
app = FastAPI(
    title=" ".join(pkg_dist.name.split("-")).title(),
    summary=str(pkg_dist.metadata.json.get("summary")),
    description=str(pkg_dist.metadata.json.get("description")),
    version=pkg_dist.version,
    lifespan=lifespan,
)
FastAPIInstrumentor.instrument_app(
    app,
    tracer_provider=telemetry.tracer_provider,
    meter_provider=telemetry.meter_provider,
)


@app.put("/")
async def get_buyers_probabilities(
    fabrics: list[fabric.Fabric],
) -> list[fabric.Fabric]:
    return APP_RESOURCES.model.get_buyers_probabilities(fabrics)


@app.post("/")
async def report_buyers_status(fabrics: list[fabric.Fabric]) -> list[fabric.Fabric]:
    return APP_RESOURCES.model.report_buyers_status(fabrics)


@app.get("/healthz/startup")
async def startup_probe():
    return APP_RESOURCES.healthz


@app.get("/healthz/liveness")
async def liveness_probe():
    return APP_RESOURCES.healthz


@app.get("/healthz/readiness")
async def readiness_probe():
    if isinstance(APP_RESOURCES.model, models.NullModel):
        raise HTTPException(status_code=status.HTTP_425_TOO_EARLY)
    return APP_RESOURCES.healthz
