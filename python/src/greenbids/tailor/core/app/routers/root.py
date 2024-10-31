from fastapi import APIRouter, Response
from greenbids.tailor.core import fabric, telemetry
from .. import resources

router = APIRouter(tags=["Main"])

_invokation_count = telemetry.meter.create_counter("greenbids_tailor_invokation_count")
_fabrics_count = telemetry.meter.create_counter("greenbids_tailor_fabrics_count")


@router.put("/")
async def get_buyers_probabilities(
    fabrics: dict[str, fabric.Fabric], response: Response
) -> dict[str, fabric.Fabric]:
    """Compute the probability of the buyers to provide a bid.

    This must be called for each adcall.
    Only the feature map attribute of the fabrics needs to be present.
    The prediction attribute will be populated in the returned response.
    """
    inst = resources.get_instance()
    results = inst.gb_model.get_buyers_probabilities(fabrics)
    is_exploration = False
    for k, f in results.items():
        is_exploration = is_exploration or f.prediction.is_exploration
        _fabrics_count.add(
            1,
            attributes={
                "greenbids.tailor.model_name": inst.gb_model_name,
                "greenbids.tailor.fabric_id": k,
                "greenbids.tailor.should_send": f.prediction.should_send,
            },
        )
    _invokation_count.add(
        1,
        {
            "greenbids.tailor.model_name": inst.gb_model_name,
            "greenbids.tailor.is_exploration": is_exploration,
        },
    )

    response.headers["greenbids-tailor-is-exploration"] = str(is_exploration)
    response.headers["greenbids-tailor-model-name"] = inst.gb_model_name
    return results


@router.post("/")
async def report_buyers_status(
    fabrics: dict[str, fabric.Fabric],
) -> dict[str, fabric.Fabric]:
    """Train model according to actual outcome.

    This must NOT be called for each adcall, but only for exploration ones.
    All fields of the fabrics need to be set.
    Returns the same data than the input.
    """
    return resources.get_instance().gb_model.report_buyers_status(fabrics)
