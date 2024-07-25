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
    is_exploration: bool = True
    """Should this opportunity be used as exploration traffic"""

    @pydantic.computed_field
    @property
    def should_send(self) -> bool:
        """Should this opportunity be forwarded to the buyer?"""
        return self.is_exploration or (self.score > self.threshold)


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
