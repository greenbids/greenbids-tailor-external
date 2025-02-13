from collections import Counter

from fastapi import APIRouter
from greenbids.tailor.core import fabric, telemetry, _version
from .. import resources


_meter = telemetry.meter_provider.get_meter(
    "greenbids.tailor", version=_version.version
)
_request_size = _meter.create_histogram(
    "greenbids.tailor.request.size", "1", "Measure the number of items in the request"
)
_response_size = _meter.create_histogram(
    "greenbids.tailor.response.size", "1", "Measure the number of items in the response"
)

router = APIRouter(tags=["Main"])


@router.put("/")
async def get_buyers_probabilities(
    fabrics: list[fabric.Fabric],
) -> list[fabric.Fabric]:
    """Compute the probability of the buyers to provide a bid.

    This must be called for each adcall.
    Only the feature map attribute of the fabrics needs to be present.
    The prediction attribute will be populated in the returned response.
    """
    _request_size.record(len(fabrics), {"http.request.method": "PUT"})
    res = resources.get_instance().gb_model.get_buyers_probabilities(fabrics)
    is_exploration_label = next(iter(res), fabric.Fabric()).prediction.is_exploration
    for should_send, count in (
        {True: 0, False: 0} | Counter(f.prediction.should_send for f in res)
    ).items():
        _response_size.record(
            count,
            {
                "http.request.method": "PUT",
                "greenbids.tailor.should_send": str(should_send),
                "greenbids.tailor.is_exploration": str(is_exploration_label),
            },
        )
    return res


@router.post("/")
async def report_buyers_status(
    fabrics: list[fabric.Fabric],
) -> list[fabric.Fabric]:
    """Train model according to actual outcome.

    This must NOT be called for each adcall, but only for exploration ones.
    All fields of the fabrics need to be set.
    Returns the same data than the input.
    """
    _request_size.record(len(fabrics), {"http.request.method": "POST"})
    return resources.get_instance().gb_model.report_buyers_status(fabrics)
