import random
import typing

import pydantic
from greenbids.tailor.core.fabric import Fabric
from polyfactory.factories import TypedDictFactory

import locust


class Tailor(locust.HttpUser):
    adapter = pydantic.TypeAdapter(list[Fabric])

    class FeatureMap(typing.TypedDict):
        bidder: str

        hostname: str
        adUnitCode: str

        country: str
        device: str
        browser: str

    class FeaturesFactory(TypedDictFactory[FeatureMap]): ...

    @locust.task
    def nominal(self):
        response = self.client.put(
            "",
            json=self.adapter.dump_python(
                [
                    Fabric(feature_map=dict(self.FeaturesFactory.build()))
                    for _ in range(random.randint(0, 10))
                ]
            ),
        )
        fabrics = self.adapter.validate_json(response.text)
        for f in fabrics:
            f.ground_truth.has_response = random.choice([True, False])
        response = self.client.post("", json=self.adapter.dump_python(fabrics))


class Probes(locust.HttpUser):
    wait_time = locust.between(10, 15)

    @locust.task
    def test_startup(self):
        self.client.get("/healthz/startup")

    @locust.task
    def test_readiness(self):
        self.client.get("/healthz/readiness")

    @locust.task
    def test_liveness(self):
        self.client.get("/healthz/liveness")
