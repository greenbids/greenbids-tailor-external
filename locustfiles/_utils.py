import typing

import polyfactory


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
