import typing
import pydantic
import pydantic.alias_generators


_BaseConfig = pydantic.ConfigDict(
    alias_generator=pydantic.alias_generators.to_camel,
    populate_by_name=True,
    use_attribute_docstrings=True,
)

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


class GroundTruth(typing.TypedDict):
    __pydantic_config__ = _BaseConfig  # type: ignore

    """Actual outcome of the opportunity"""
    has_response: typing.Annotated[bool, pydantic.Field(default=True)]
    """Did this opportunity lead to a valid buyer response?"""


class Fabric(typing.TypedDict, total=False):
    """Main entity used to tailor the traffic.

    All fields are optional when irrelevant.
    """

    __pydantic_config__ = _BaseConfig  # type: ignore

    feature_map: dict[str, typing.Any]
    prediction: Prediction | None
    ground_truth: GroundTruth | None
