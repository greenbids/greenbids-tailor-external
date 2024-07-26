from abc import abstractmethod
from importlib import metadata
from abc import ABC
import subprocess
import io
import os

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

    def dump(self, fp: io.BytesIO) -> None:
        pass

    @classmethod
    def load(cls, fp: io.BytesIO) -> "Model":
        return cls()


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


REGISTRY = metadata.entry_points(group="greenbids-tailor-models")


def fetch(target: str):
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
    REGISTRY.clear()
    REGISTRY.extend(metadata.entry_points(group="greenbids-tailor-models"))


def get_instance():
    return NullModel()
