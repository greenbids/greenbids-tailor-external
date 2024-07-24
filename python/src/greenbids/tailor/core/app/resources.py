import datetime
import logging
import math
import os
import time

import pydantic
from greenbids.tailor.core import models

_logger = logging.getLogger(__name__)


class AppResources(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    gb_model_name: str = "None"
    gb_model: models.Model = pydantic.Field(default=models.NullModel(), exclude=True)
    start: datetime.datetime = datetime.datetime.min
    start_monotonic: float = pydantic.Field(default=math.nan, exclude=True)

    @pydantic.computed_field
    @property
    def uptime_second(self) -> float:
        return time.monotonic() - self.start_monotonic

    def setup(self) -> "AppResources":
        self.gb_model_name = str(os.environ.get("GREENBIDS_TAILOR_MODEL_NAME"))
        self.gb_model = models.REGISTRY[self.gb_model_name].load().get_instance()
        self.start_monotonic = time.monotonic()
        self.start = datetime.datetime.now(datetime.timezone.utc)
        _logger.info(self.model_dump_json())
        return self


APP_RESOURCES = AppResources()
