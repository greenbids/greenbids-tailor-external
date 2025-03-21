import json
import hashlib
import random

import locust

from _utils import AdRequestFactory


class Rtb(locust.FastHttpUser):
    """Traffic shaping testing."""

    wait_time = locust.constant_throughput(100)

    @locust.task
    def handleAdRequest(self):
        """Here we simulate the way an SSP may integrate with the Greenbids Tailor service."""

        # Suppose that you got an ad request as input
        ad_request = AdRequestFactory.build()

        # Build a list of features for each bidder in the ad request
        feature_maps = [
            {
                "featureMap": {
                    "bidder": bidder["name"],
                    "hasUserId": bidder.get("user_id") is not None,
                    # "publisherId": ad_request["hostname"],
                    "deviceType": ad_request["device"],
                    "country": ad_request["country"],
                    # "ua": ad_request["user_agent"],
                    # You may add whatever seems relevant to you here.
                    "SSP's_secret_ingredient": 42,
                    # Let's get in touch to allow us to craft a well suited model.
                }
            }
            for bidder in ad_request["bidders"]
        ]
        # Do a single PUT call containing the whole feature_maps list to the Greenbids Tailor service
        # The returned `fabrics` variable contains the list of features_maps with the associated predictions:
        # [{"featureMap": {...}, "prediction": {...}}, {"featureMap": {...}, prediction: {...}}, ...]
        fabrics = self.client.put("", json=feature_maps).json()

        # Do your regular calls here to send a bid requests to the selected bidders
        for fabric in fabrics:
            if not fabric["prediction"]["shouldSend"]:
                # Skip any bidder that as too few response probability
                continue

            # For selected bidders, send them a bid request and check if they returned a bid
            # hasResponse = (requests.post(bidder.url, json={...}).status_code == 200)

            # For test we simulate this deterministically (10% participation rate) with some noise (0.1%)
            hasResponse = self._get_mocked_participation(fabric)

            # Store the outcome in the fabric
            fabric["groundTruth"] = dict(hasResponse=hasResponse)

        # For a sample of calls, report the outcomes to the Greenbids Tailor POST endpoint
        if fabrics[0]["prediction"]["isTraining"]:
            # You may use a fire-and-forget mechanism
            self.client.post("", json=fabrics)

    @staticmethod
    def _get_mocked_participation(fabric: dict) -> bool:
        hasResponse = (
            hashlib.md5(
                json.dumps(fabric["featureMap"], sort_keys=True).encode()
            ).digest()[0]
            < 26
        )
        if random.random() < 0.001:  # Add some noise
            hasResponse = not hasResponse
        return hasResponse
