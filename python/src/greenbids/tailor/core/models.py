import logging
import os
import pickle
import random
import subprocess
import typing
from abc import ABC, abstractmethod

from greenbids.tailor.core import fabric

_logger = logging.getLogger(__name__)


class Model(ABC):

    @abstractmethod
    def get_buyers_probabilities(
        self,
        fabrics: list[fabric.PredictionInput],
    ) -> list[fabric.PredictionOutput]:
        raise NotImplementedError

    @abstractmethod
    def report_buyers_status(
        self,
        fabrics: list[fabric.ReportInput],
    ) -> None:
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
        fabrics: list[fabric.PredictionInput],
    ) -> list[fabric.PredictionOutput]:
        prediction = fabric.Prediction(score=1, is_exploration=(random.random() < 0.2))
        return [
            fabric.PredictionOutput(feature_map=f["feature_map"], prediction=prediction)
            for f in fabrics
        ]

    def report_buyers_status(
        self,
        fabrics: list[fabric.ReportInput],
    ) -> None:
        self._logger.debug([f.get("feature_map", {}) for f in fabrics[:1]])


ENTRY_POINTS_GROUP = "greenbids-tailor-models"


def download(target: str):
    subprocess.check_output(
        [
            "pip",
            "install",
            "--upgrade",
            "--index-url",
            os.environ.get("GREENBIDS_TAILOR_INDEX_URL", ""),
            target,
        ]
    )


def get_instance(**_):
    return NullModel()
