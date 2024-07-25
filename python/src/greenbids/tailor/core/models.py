from abc import abstractmethod
from importlib.metadata import entry_points
from abc import ABC

from greenbids.tailor.core import fabric


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


REGISTRY = entry_points(group="greenbids-tailor-models")


def get_instance():
    return NullModel()
