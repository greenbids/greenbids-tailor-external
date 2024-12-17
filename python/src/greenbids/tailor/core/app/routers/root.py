from collections import Counter

import cachetools
from fastapi import APIRouter
from greenbids.tailor.core import fabric, telemetry, _version, settings
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
_cache_info = _meter.create_counter("greenbids.tailor.cache", "1")

router = APIRouter(tags=["Main"])


_PREDICTION_CACHE = cachetools.TTLCache(
    maxsize=settings.SETTINGS.prediction_cache_size,
    ttl=settings.SETTINGS.prediction_cache_ttl_seconds,
)


@router.put("/")
async def get_buyers_probabilities(
    fabrics: tuple[fabric.Fabric, ...],
) -> tuple[fabric.Fabric, ...]:
    """Compute the probability of the buyers to provide a bid.

    This must be called for each adcall.
    Only the feature map attribute of the fabrics needs to be present.
    The prediction attribute will be populated in the returned response.
    """
    _request_size.record(len(fabrics), {"http.request.method": "PUT"})
    if fabrics not in _PREDICTION_CACHE:
        _cache_info.add(1, attributes={"result": "miss"})
        _PREDICTION_CACHE[fabrics] = (
            resources.get_instance().gb_model.get_buyers_probabilities(fabrics)
        )
    else:
        _cache_info.add(1, attributes={"result": "hit"})
    res = _PREDICTION_CACHE[fabrics]
    for should_send, count in (
        {True: 0, False: 0} | Counter(f.prediction.should_send for f in res)
    ).items():
        _response_size.record(
            count,
            {
                "http.request.method": "PUT",
                "greenbids.tailor.should_send": str(should_send),
            },
        )
    return res


@router.post("/")
async def report_buyers_status(
    fabrics: tuple[fabric.Fabric, ...],
) -> tuple[fabric.Fabric, ...]:
    """Train model according to actual outcome.

    This must NOT be called for each adcall, but only for exploration ones.
    All fields of the fabrics need to be set.
    Returns the same data than the input.
    """
    _request_size.record(len(fabrics), {"http.request.method": "POST"})
    return resources.get_instance().gb_model.report_buyers_status(fabrics)
