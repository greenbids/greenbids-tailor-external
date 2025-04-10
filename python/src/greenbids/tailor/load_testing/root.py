import locust

from greenbids.tailor.load_testing._utils import AdRequestFactory


class Root(locust.FastHttpUser):

    weight = 1e-6

    def on_start(self) -> None:
        ad_request = AdRequestFactory.build()

        self.fabrics = [
            {
                "featureMap": {
                    "bidder": bidder["name"],
                    "userSynced": bidder.get("user_id") is not None,
                    "hostname": ad_request["hostname"],
                    "device": ad_request["device"],
                },
                "prediction": {"isExploration": True, "score": 1, "threshold": -1},
                "groundTruth": {"hasResponse": True},
            }
            for bidder in ad_request["bidders"]
        ]
        return super().on_start()

    @locust.task(100)
    def request(self):
        self.client.put("", json=self.fabrics)

    @locust.task(20)
    def report(self):
        self.client.post("", json=self.fabrics)
