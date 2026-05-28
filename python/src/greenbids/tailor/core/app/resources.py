import datetime
import functools
import glob
import io
import logging
import os
import tempfile
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

    @property
    def _dump_prefix(self):
        return f"gb-tailor_{self.gb_model_name}_"

    def _should_refresh(self) -> bool:
        if self._gb_model is None:
            return True

        try:
            rsp = requests.get(
                settings.authenticated_index_url.geturl()
                + f"/_commands/{settings.api_user}-{self.gb_model_name}.json"
            )
            rsp.raise_for_status()
            rsp = rsp.json()
            if datetime.datetime.fromisoformat(rsp["ts"]) < self._last_refresh:
                _logger.debug("Model already refreshed on %s", self._last_refresh)
                return False
        except Exception:
            _logger.debug("Fail to check model commands", exc_info=True)
            return False

        return True

    def _get_model_dump(self) -> io.BytesIO | None:
        buf = io.BytesIO()
        if self._gb_model is not None:
            _logger.info("Reloading model from in-memory dump")
            self._gb_model.dump(buf)
            return buf

        if existing_model_dump := next(
            iter(
                sorted(
                    glob.glob(f"{settings.data_directory}/{self._dump_prefix}*"),
                    reverse=True,
                )
            ),
            None,
        ):
            _logger.info("Reloading model from %s", existing_model_dump)
            with open(existing_model_dump, "rb") as fp:
                buf.write(fp.read())
            return buf

        return None

    def refresh_model(self) -> None:
        if not self._should_refresh():
            return

        kwargs = {}
        if (buf := self._get_model_dump()) is not None:
            buf.seek(0)
            kwargs["fp"] = buf

        self._gb_model = models.load(self.gb_model_name, **kwargs)
        self._last_refresh = datetime.datetime.now(datetime.timezone.utc)
        _logger.info("Model %s loaded", self.gb_model_name)

    def save_model(self) -> str | None:
        if self._gb_model is None:
            return None

        ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        os.makedirs(settings.data_directory, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "wb",
            prefix=f"{self._dump_prefix}{ts:.0f}_",
            dir=settings.data_directory,
            delete=False,
        ) as fp:
            _logger.info("Model dumped to %s", fp.name)
            self.gb_model.dump(fp)  # type: ignore
            return fp.name


@functools.lru_cache(maxsize=1)
def get_instance() -> AppResources:
    return AppResources()
