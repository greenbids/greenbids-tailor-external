import contextlib
import datetime
import logging
from importlib.metadata import distribution

from fastapi import FastAPI
from greenbids.tailor.core import _version, telemetry, logging_ as gb_logging
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from . import profiler, resources, tasks, exceptions
from .routers import healthz, ping, root

_logger = logging.getLogger(__name__)

@contextlib.asynccontextmanager
async def _lifespan(app: FastAPI):
    _setup_logging()
    if resources.get_instance.cache_info().currsize > 0:
        _logger.warning("A resource object was initialized before app startup")
    app_resources = resources.get_instance()
    _setup_telemetry()
    await tasks.repeat_every(
        seconds=app_resources.gb_model_refresh_period.total_seconds(),
        logger=_logger.getChild("model_reload"),
    )(app_resources.refresh_model)()
    with profiler.profile():
        yield


def _setup_telemetry():
    from opentelemetry.metrics import CallbackOptions, Observation

    meter = telemetry.meter_provider.get_meter(
        "greenbids.tailor", version=_version.version
    )

    def uptime_cb(options: CallbackOptions) -> list[Observation]:
        app_res = resources.get_instance()
        return [
            Observation(
                app_res.uptime_second,
                {
                    k: str(v)
                    for k, v in app_res.model_dump(exclude={"uptime_second"}).items()
                },
            )
        ]

    meter.create_observable_gauge("greenbids.tailor.uptime", (uptime_cb,), unit="s")


def _setup_logging():
    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(logging.Formatter(fmt=logging.BASIC_FORMAT))

    logging.root.addHandler(stderr_handler)
    logging.root.addHandler(telemetry.handler)
    uvicorn_logger = logging.getLogger("uvicorn.access")
    uvicorn_logger.addFilter(gb_logging.HttpAccessFilter())
    uvicorn_logger.addFilter(
        gb_logging.RateLimitingFilter(
            30, datetime.timedelta(minutes=1), logger=f"{__name__}.uvicorn.access"
        )
    )

pkg_dist = distribution("greenbids-tailor")
app = FastAPI(
    title=" ".join(pkg_dist.name.split("-")).title(),
    summary=str(pkg_dist.metadata.json.get("summary")),
    description=str(pkg_dist.metadata.json.get("description")),
    version=pkg_dist.version,
    lifespan=_lifespan,
    exception_handlers=exceptions.EXCEPTION_HANDLERS,
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
