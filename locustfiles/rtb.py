import random

import locust

from _utils import AdRequestFactory


class Rtb(locust.FastHttpUser):
    """Traffic shaping testing."""

    @locust.task
    def handleAdRequest(self):
        """Here we simulate the way an SSP may integrate with the Greenbids Tailor service."""

        # Suppose that you got an ad request as input
        ad_request = AdRequestFactory.build()

        # Build a list of features for each bidder in the ad request
        fabrics = {
            bidder["name"]: {
                "featureMap": {
                    "bidder": bidder["name"],
                    "userSynced": bidder.get("user_id") is not None,
                    "hostname": ad_request["hostname"],
                    "device": ad_request["device"],
                    # You may add whatever seems relevant to you here.
                    "SSP's_secret_ingredient": 42,
                    # Let's get in touch to allow us to craft a well suited model.
                }
            }
            for bidder in ad_request["bidders"]
        }
        # Do a single call to the Greenbids Tailor service
        fabrics = self.client.put("", json=fabrics).json()
        # Prepare a flag to know if you must make the POST call
        is_exploration = False

        # Do your regular calls here to send a bid requests to the selected bidders
        for fabric in fabrics.values():
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

            is_exploration = is_exploration or fabric["prediction"]["isExploration"]

        # For a sample of calls, report the outcomes to the Greenbids Tailor POST endpoint
        if is_exploration:
            # You may use a fire-and-forget mechanism
            self.client.post("", json=fabrics)
