from collections import abc
import uuid

import pydantic
import pydantic.alias_generators


class _CamelSerialized(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.alias_generators.to_camel,
        populate_by_name=True,
        use_attribute_docstrings=True,
        extra="ignore",
    )


class FeatureMap(pydantic.RootModel):
    """Mapping describing the current opportunity."""
    root: dict[str, bool | int | float | bytes | str] = pydantic.Field(
        default_factory=dict
    )


class WithFeatureMap(_CamelSerialized):
    feature_map: FeatureMap = pydantic.Field(default_factory=FeatureMap)


class Prediction(_CamelSerialized):
    """Result of the shaping process."""
    score: float = -1
    """Confidence score returned by the model"""
    score_type: str = "UNDEFINED"
    """How the score was computed"""
    threshold: float = -1
    """Confidence threshold used to binarize the outcome"""
    tailor_id: uuid.UUID = pydantic.Field(default_factory=lambda: uuid.UUID(int=0))
    """ID identifying this call"""
    exploration_rate: float = 1
    """Which proportion of requests will be exploration ones"""
    training_rate: float = 0
    """Which proportion of requests will be used for training"""

    def _sample(self, rate: float) -> bool:
        randomness_value = self.tailor_id.node
        threshold_value = int(0x1_0000_0000_0000 * (1 - rate))
        return randomness_value >= threshold_value

    @pydantic.computed_field
    @property
    def is_exploration(self) -> bool:
        """Should this opportunity be used as exploration traffic"""
        try:
            return self._sample(self.exploration_rate)
        except ValueError:
            return True

    @pydantic.computed_field
    @property
    def is_training(self) -> bool:
        """Should this opportunity be used to train the model"""
        try:
            return self._sample(self.training_rate)
        except ValueError:
            return False

    @pydantic.computed_field
    @property
    def should_send(self) -> bool:
        """Should this opportunity be forwarded to the buyer?"""
        return self.is_exploration or (self.score >= self.threshold)


class WithPrediction(_CamelSerialized):
    prediction: Prediction = pydantic.Field(default_factory=Prediction)


class GroundTruth(_CamelSerialized):
    """Actual outcome of the opportunity"""
    has_response: bool = True
    """Did this opportunity lead to a valid buyer response?"""


class PredictionFabric(_CamelSerialized):
    """Input for prediction requests"""

    feature_map: FeatureMap = pydantic.Field(default_factory=FeatureMap)


class PredictedFabric(PredictionFabric):
    """Output of prediction requests"""

    prediction: Prediction = pydantic.Field(default_factory=Prediction)


class TrainingFabric(PredictedFabric):
    """Input for training requests"""

    ground_truth: GroundTruth = pydantic.Field(default_factory=GroundTruth)


def should_report(fabrics: abc.Sequence[PredictedFabric]) -> bool:
    """Does a request should be sent to report endpoints.

    Returns `True` if **all (and at least one)** fabrics are exploration and training one, else `False`.
    """
    return bool(fabrics) and all(
        (f.prediction.is_exploration and f.prediction.is_training) for f in fabrics
    )
