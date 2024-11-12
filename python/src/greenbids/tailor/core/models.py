from importlib import metadata
import importlib
import logging
import os
import pickle
import subprocess
import typing
from abc import ABC, abstractmethod
from urllib.parse import urlsplit

from greenbids.tailor.core import fabric
from greenbids.tailor.core.app import settings


_logger = logging.getLogger(__name__)


class UnexpectedReport(ValueError):
    """Raised when the report was called while it is not expected."""

    def __init__(self, *args: object, fabrics: list[fabric.Fabric]) -> None:
        super().__init__(*args)
        self.fabrics = fabrics


class Model(ABC):

    @abstractmethod
    def get_buyers_probabilities(
        self,
        fabrics: list[fabric.Fabric],
    ) -> list[fabric.Fabric]:
        raise NotImplementedError

    @abstractmethod
    def report_buyers_status(
        self,
        fabrics: list[fabric.Fabric],
    ) -> list[fabric.Fabric]:
        raise NotImplementedError

    def dump(self, fp: typing.BinaryIO) -> None:
        pickle.dump(self, fp)

    @classmethod
    def load(cls, fp: typing.BinaryIO) -> "Model":
        return pickle.load(fp)


class NullModel(Model):
    """Dummy model that never filter."""

    def __init__(self):
        self._logger = _logger.getChild("null")

    def get_buyers_probabilities(
        self,
        fabrics: list[fabric.Fabric],
    ) -> list[fabric.Fabric]:
        prediction = fabric.Prediction(exploration_rate=0.2)
        return [f.model_copy(update=dict(prediction=prediction)) for f in fabrics]

    def report_buyers_status(
        self,
        fabrics: list[fabric.Fabric],
    ) -> list[fabric.Fabric]:
        if not fabric.should_report(fabrics):
            raise UnexpectedReport(fabrics=fabrics)
        self._logger.debug([f.feature_map.root for f in fabrics[:1]])
        return fabrics


ENTRY_POINTS_GROUP = "greenbids-tailor-models"


def load(gb_model_name: str, **kwargs):
    if gb_model_name == str(None) or settings.get_settings().download_disabled:
        _logger.debug("No model to download")
    else:
        _download(gb_model_name)
        importlib.invalidate_caches()

    return (
        metadata.entry_points(group=ENTRY_POINTS_GROUP)[gb_model_name]
        .load()
        .get_instance(**kwargs)
    )


def _download(target: str):
    """Download a model from private Python registry

    Args:
        target (str): Simple name of the model
    """
    index_url = urlsplit(settings.get_settings().index_url)
    netloc = index_url.netloc.split("@")[-1]
    index_url = index_url._replace(
        netloc="{}:{}@{}".format(
            settings.get_settings().api_user,
            settings.get_settings().api_key,
            netloc,
        )
    )
    args = [
        "pip",
        "install",
        "--upgrade",
        "--index-url",
        index_url.geturl(),
        "--extra-index-url",
        "https://pypi.org/simple",
        f"greenbids-tailor-models-{target}",
    ]
    _logger.debug(subprocess.check_output(args).decode())


def get_instance(**_):
    return NullModel()
