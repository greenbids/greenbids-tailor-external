import typing
import pydantic
import pydantic.alias_generators


_BaseConfig = pydantic.ConfigDict(
    alias_generator=pydantic.alias_generators.to_camel,
    populate_by_name=True,
    use_attribute_docstrings=True,
)
class _BaseTypedDict(typing.TypedDict):
    __pydantic_config__ = _BaseConfig  # type: ignore


FeatureMap: typing.TypeAlias = dict[str, typing.Any]


class Prediction(pydantic.BaseModel):
    model_config = _BaseConfig

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


class GroundTruth(_BaseTypedDict):
    """Actual outcome of the opportunity"""
    has_response: typing.Annotated[bool, pydantic.Field(default=True)]
    """Did this opportunity lead to a valid buyer response?"""


class ReportInput(_BaseTypedDict):
    feature_map: FeatureMap
    prediction: Prediction
    ground_truth: GroundTruth


class PredictionInput(_BaseTypedDict):
    feature_map: FeatureMap


class PredictionOutput(_BaseTypedDict):
    feature_map: FeatureMap
    prediction: Prediction
