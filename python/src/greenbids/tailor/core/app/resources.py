import datetime
import functools
import io
import logging
import os
import time

import pydantic
import requests
from greenbids.tailor.core import models, version
from greenbids.tailor.core.settings import settings

_logger = logging.getLogger(__name__)


class ModelNotReady(AttributeError):
    def __init__(self, *args: object, model_name: str, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.model_name = model_name


class AppResources(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    gb_model_name: str = pydantic.Field(
        default_factory=lambda: str(os.environ.get("GREENBIDS_TAILOR_MODEL_NAME"))
    )
    gb_model_refresh_period: datetime.timedelta = pydantic.Field(
        default_factory=lambda: settings.gb_model_refresh_period
    )
    start: datetime.datetime = pydantic.Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    profiling_output: str = pydantic.Field(
        default_factory=lambda: os.environ.get("GREENBIDS_TAILOR_PROFILE", "")
    )
    _start_monotonic: float = pydantic.PrivateAttr(default_factory=time.monotonic)
    _gb_model: models.Model | None = None
    _last_refresh: datetime.datetime = pydantic.PrivateAttr(
        default_factory=lambda: datetime.datetime.min.replace(
            tzinfo=datetime.timezone.utc
        )
    )

    def __init__(self, **data):
        super().__init__(**data)
        _logger.info(self.model_dump_json())

    @property
    def gb_model(self) -> models.Model:
        if self._gb_model is None:
            raise ModelNotReady(
                model_name=self.gb_model_name, name="gb_model", obj=self
            )
        return self._gb_model

    @pydantic.computed_field
    @property
    def uptime_second(self) -> float:
        return time.monotonic() - self._start_monotonic

    @pydantic.computed_field
    @property
    def core_version(self) -> str:
        return version

    @pydantic.computed_field
    @property
    def is_ready(self) -> bool:
        return self._gb_model is not None

    def refresh_model(self) -> None:
        if self._gb_model is not None:
            try:
                rsp = requests.get(
                    settings.authenticated_index_url.geturl()
                    + f"/_commands/{settings.api_user}-{self.gb_model_name}.json"
                ).json()
                if datetime.datetime.fromisoformat(rsp["ts"]) < self._last_refresh:
                    _logger.debug("Model already refreshed on %s", self._last_refresh)
                    return
            except Exception:
                _logger.debug("Fail to check model commands", exc_info=True)
                return

        kwargs = {}
        try:
            buf = io.BytesIO()
            self.gb_model.dump(buf)
            buf.seek(0)
            kwargs["fp"] = buf
        except ModelNotReady:
            pass
        self._gb_model = models.load(self.gb_model_name, **kwargs)
        self._last_refresh = datetime.datetime.now(datetime.timezone.utc)
        _logger.info("Model %s loaded", self.gb_model_name)


@functools.lru_cache(maxsize=1)
def get_instance() -> AppResources:
    return AppResources()
