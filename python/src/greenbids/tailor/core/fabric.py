import pydantic
import pydantic.alias_generators


class _CamelSerialized(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        alias_generator=pydantic.alias_generators.to_camel, populate_by_name=True
    )


class FeatureMap(_CamelSerialized, pydantic.RootModel):
    root: dict[str, bool | int | float | bytes | str] = pydantic.Field(
        default_factory=dict
    )


class WithFeatureMap(_CamelSerialized):

    feature_map: FeatureMap = pydantic.Field(default_factory=FeatureMap)


class Prediction(_CamelSerialized):
    probability: float = -1
    threshold: float = -1
    is_exploration: bool = True

    @pydantic.computed_field
    @property
    def should_send(self) -> bool:
        return self.is_exploration or (self.probability > self.threshold)


class WithPrediction(_CamelSerialized):
    prediction: Prediction = pydantic.Field(default_factory=Prediction)


class GroundTruth(_CamelSerialized):
    has_response: bool = True


class WithGroundTruth(_CamelSerialized):
    ground_truth: GroundTruth = pydantic.Field(default_factory=GroundTruth)


class Fabric(WithFeatureMap, WithPrediction, WithGroundTruth):
    pass
