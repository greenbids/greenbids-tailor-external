import os
import pickle
import subprocess
import typing
from abc import ABC, abstractmethod

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

    def dump(self, fp: typing.BinaryIO) -> None:
        pickle.dump(self, fp)

    @classmethod
    def load(cls, fp: typing.BinaryIO) -> "Model":
        return pickle.load(fp)


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
