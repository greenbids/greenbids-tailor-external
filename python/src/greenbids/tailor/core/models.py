import logging
from typing import Protocol
from abc import abstractmethod

from greenbids.tailor.core import fabric

_logger = logging.getLogger(__name__)


class Model(Protocol):
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


class NullModel(Model):
    def get_buyers_probabilities(
        self,
        fabrics: list[fabric.Fabric],
    ) -> list[fabric.Fabric]:
        return fabrics

    def report_buyers_status(
        self,
        fabrics: list[fabric.Fabric],
    ) -> list[fabric.Fabric]:
        return fabrics


def get_model() -> Model:
    import os
    from importlib.metadata import entry_points

    model_name = os.environ.get("GREENBIDS_TAILOR_MODEL_NAME", "default")
    _logger.info("Loading model '%s'", model_name)

    models = entry_points(group="greenbids-tailor-models")
    return models[model_name].load().get_instance()
