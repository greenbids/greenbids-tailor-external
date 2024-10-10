import datetime
import functools
from importlib import metadata
import logging
import os
import time
import io

import pydantic
from greenbids.tailor.core import models, version

_logger = logging.getLogger(__name__)


def _default_refresh_period() -> datetime.timedelta:
    return (
        datetime.timedelta(seconds=float(seconds))
        if (
            seconds := os.environ.get(
                "GREENBIDS_TAILOR_MODEL_REFRESH_SECONDS",
            )
        )
        is not None
        else datetime.timedelta.max
    )


class AppResources(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    gb_model_name: str = pydantic.Field(
        default_factory=lambda: str(os.environ.get("GREENBIDS_TAILOR_MODEL_NAME"))
    )
    gb_model_refresh_period: datetime.timedelta = pydantic.Field(
        default_factory=_default_refresh_period
    )
    start: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    profiling_output: str = pydantic.Field(
        default_factory=lambda: os.environ.get("GREENBIDS_TAILOR_PROFILE", "")
    )
    _start_monotonic: float = pydantic.PrivateAttr(default_factory=time.monotonic)
    _gb_model: models.Model

    def __init__(self, **data):
        super().__init__(**data)
        self._gb_model = (
            metadata.entry_points(group=models.ENTRY_POINTS_GROUP)[self.gb_model_name]
            .load()
            .get_instance()
        )
        _logger.info(self.model_dump_json())

    @property
    def gb_model(self) -> models.Model:
        return self._gb_model

    @pydantic.computed_field
    @property
    def uptime_second(self) -> float:
        return time.monotonic() - self._start_monotonic

    @pydantic.computed_field
    @property
    def core_version(self) -> str:
        return version

    def refresh_model(self) -> "AppResources":
        buf = io.BytesIO()
        self.gb_model.dump(buf)
        buf.seek(0)
        self._gb_model = (
            metadata.entry_points(group=models.ENTRY_POINTS_GROUP)[self.gb_model_name]
            .load()
            .get_instance(fp=buf)
        )
        return self


@functools.lru_cache(maxsize=1)
def get_instance() -> AppResources:
    return AppResources()
