from abc import abstractmethod
from importlib.metadata import entry_points
from abc import ABC

from greenbids.tailor.core import fabric


class Model(ABC):

    class GetBuyersProbabilitiesInput(fabric.WithFeatureMap):
        pass

    class GetBuyersProbabilitiesOutput(fabric.WithPrediction, fabric.WithFeatureMap):
        pass

    @abstractmethod
    def get_buyers_probabilities(
        self,
        fabrics: list[GetBuyersProbabilitiesInput],
    ) -> list[GetBuyersProbabilitiesOutput]:
        raise NotImplementedError

    class ReportBuyersStatusInput(
        fabric.WithGroundTruth, fabric.WithPrediction, fabric.WithFeatureMap
    ):
        pass

    class ReportBuyersStatusOutput(
        fabric.WithGroundTruth, fabric.WithPrediction, fabric.WithFeatureMap
    ):
        pass

    @abstractmethod
    def report_buyers_status(
        self,
        fabrics: list[ReportBuyersStatusInput],
    ) -> list[ReportBuyersStatusOutput]:
        raise NotImplementedError


class NullModel(Model):

    def get_buyers_probabilities(
        self,
        fabrics: list[Model.GetBuyersProbabilitiesInput],
    ) -> list[Model.GetBuyersProbabilitiesOutput]:
        return [Model.GetBuyersProbabilitiesOutput(**f.model_dump()) for f in fabrics]

    def report_buyers_status(
        self,
        fabrics: list[Model.ReportBuyersStatusInput],
    ) -> list[Model.ReportBuyersStatusOutput]:
        return [Model.ReportBuyersStatusOutput(**f.model_dump()) for f in fabrics]


REGISTRY = entry_points(group="greenbids-tailor-models")


def get_instance():
    return NullModel()
