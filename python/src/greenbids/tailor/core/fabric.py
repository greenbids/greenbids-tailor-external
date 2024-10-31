import uuid

import pydantic
import pydantic.alias_generators


class _CamelSerialized(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.alias_generators.to_camel,
        populate_by_name=True,
        use_attribute_docstrings=True,
    )


class FeatureMap(_CamelSerialized, pydantic.RootModel):
    """Mapping describing the current opportunity."""
    root: dict[str, bool | int | float | bytes | str] = pydantic.Field(
        default_factory=dict
    )


class Prediction(_CamelSerialized):
    """Result of the shaping process."""
    score: float = -1
    """Confidence score returned by the model"""
    threshold: float = -1
    """Confidence threshold used to binarize the outcome"""
    tailor_id: uuid.UUID = pydantic.Field(default_factory=uuid.uuid4)
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


class GroundTruth(_CamelSerialized):
    """Actual outcome of the opportunity"""
    has_response: bool = True
    """Did this opportunity lead to a valid buyer response?"""


class Fabric(_CamelSerialized):
    """Main entity used to tailor the traffic.

    All fields are optional when irrelevant.
    """

    feature_map: FeatureMap = pydantic.Field(default_factory=FeatureMap)
    prediction: Prediction = pydantic.Field(default_factory=Prediction)
    ground_truth: GroundTruth = pydantic.Field(default_factory=GroundTruth)
