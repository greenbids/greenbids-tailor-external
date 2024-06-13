import typing
import pydantic
import pydantic.alias_generators


class _CamelSerialized(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.alias_generators.to_camel, populate_by_name=True
    )


class Prediction(_CamelSerialized):
    probability: float = -1
    threshold: float = -1

    @pydantic.computed_field
    @property
    def should_send(self) -> bool:
        return self.probability > self.threshold


class GroundTruth(_CamelSerialized):
    has_response: bool = True


class Fabric(_CamelSerialized):
    feature_map: typing.Annotated[
        dict[str, typing.Any], pydantic.Field(default_factory=dict)
    ]
    prediction: typing.Annotated[Prediction, pydantic.Field(default_factory=Prediction)]
    ground_truth: typing.Annotated[
        GroundTruth, pydantic.Field(default_factory=GroundTruth)
    ]
