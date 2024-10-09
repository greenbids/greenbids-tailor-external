import random
import typing

import locust
import polyfactory


class Root(locust.FastHttpUser):
    """Traffic shaping testing."""

    @locust.task
    def handleAdRequest(self):
        """Here we simulate the way an SSP may integrate with the Greenbids Tailor service."""

        # Suppose that you got an ad request as input
        ad_request = AdRequestFactory.build()

        # Build a list of features for each bidder in the ad request
        feature_maps = [
            {
                "bidder": bidder["name"],
                "userSynced": bidder.get("user_id") is not None,
                "hostname": ad_request["hostname"],
                "device": ad_request["device"],
                # You may add whatever seems relevant to you here.
                "SSP's_secret_ingredient": 42,
                # Let's get in touch to allow us to craft a well suited model.
            }
            for bidder in ad_request["bidders"]
        ]
        # Do a single call to the Greenbids Tailor service
        fabrics = self.client.put("", json=feature_maps).json()

        # Do your regular calls here to send a bid requests to the selected bidders
        for fabric in fabrics:
            if not fabric["prediction"]["shouldSend"]:
                # Skip any bidder that as too few response probability
                continue

            # For selected bidders, send them a bid request
            # rsp = requests.post(bidder.url, json={...})

            # Bidder may or may not return a bid (for test we simulate this randomly)
            # hasResponse = (rsp.status_code != 204)
            hasResponse = random.choice([True, False])

            # Store the outcome in the fabric
            fabric["groundTruth"] = dict(hasResponse=hasResponse)

        # For a sample of calls, report the outcomes to the Greenbids Tailor POST endpoint
        if fabrics[0]["prediction"]["isExploration"]:
            # You may use a fire-and-forget mechanism
            self.client.post("", json=fabrics)


class Bidder(typing.TypedDict):
    """A simplified example of bidder specific parameters passed in an ad request."""

    name: str
    """The name/ID of the bidder"""
    user_id: str | None
    """What is the user ID of the current user on DSP's side (user sync)"""


class AdRequest(typing.TypedDict):
    """A simplified example of an ad request that an SSP may handle."""

    bidders: list[Bidder]
    """The full list of elligible DSPs for the auction."""

    hostname: str
    """Hostname of the publisher generating this ad request"""

    device: str
    """Device used by the user visiting the publisher's site"""


class AdRequestFactory(polyfactory.factories.TypedDictFactory[AdRequest]):
    """Utility object to generate random AdRequests"""

    __randomize_collection_length__ = True
    __min_collection_length__ = 2
    """Minimal number of bidders"""
    __max_collection_length__ = 15
    """Maximal number of bidders"""

    pass
