import pydantic


class Imp(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")


class BidRequest(pydantic.BaseModel):
    """Top-level bid request object.

    The top-level bid request object contains a globally unique bid request or auction ID.
    This “id” attribute is required as is at least one “imp” (i.e., impression) object.
    Other attributes are optional since an exchange may establish default values.
    """

    model_config = pydantic.ConfigDict(extra="allow")

    id: str
    imp: list[Imp]


class Bid(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")


class SeatBid(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    bid: list[Bid]


class BidResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    id: str
    seatbid: list[SeatBid]
