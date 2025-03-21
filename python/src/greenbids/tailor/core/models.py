import importlib
import logging
import os
import pickle
import subprocess
import typing
import uuid
import sys
from abc import ABC, abstractmethod
from importlib import metadata
from urllib.parse import urlsplit

from filelock import FileLock

from greenbids.tailor.core import fabric

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
        prediction = fabric.Prediction(
            exploration_rate=0.2, training_rate=0.2, tailor_id=uuid.uuid4()
        )
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
    if (
        gb_model_name == str(None)
        or os.environ.get("GREENBIDS_TAILOR_DOWNLOAD_DISABLED", "").lower() == "true"
    ):
        _logger.debug("No model to download")
    else:
        _download(gb_model_name)
        importlib.invalidate_caches()

    ep = metadata.entry_points(group=ENTRY_POINTS_GROUP)[gb_model_name.split("=")[0]]
    for name in {m for m in sys.modules if str(m).startswith(ep.value)}:
        del sys.modules[name]
    mod = ep.load()
    return mod.get_instance(**kwargs)

_download_lock = FileLock("/tmp/greenbids-tailor-download.lock")
def _download(target: str):
    """Download a model from private Python registry

    Args:
        target (str): Simple name of the model
    """
    index_url = urlsplit(os.environ.get("GREENBIDS_TAILOR_INDEX_URL", ""))
    netloc = index_url.netloc.split("@")[-1]
    index_url = index_url._replace(
        netloc="{}:{}@{}".format(
            os.environ.get("GREENBIDS_TAILOR_API_USER", "nobody"),
            os.environ.get("GREENBIDS_TAILOR_API_KEY", ""),
            netloc,
        )
    )
    _logger.info("Downloading model %s...", target)
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
    with _download_lock:
        _logger.debug("Download lock acquired")
        output = subprocess.check_output(args).decode()
    _logger.debug(output)


def get_instance(**_):
    return NullModel()
