from fastapi import APIRouter
from greenbids.tailor.core import fabric
from .. import resources

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
    return resources.get_instance().gb_model.get_buyers_probabilities(fabrics)


@router.post("/")
async def report_buyers_status(
    fabrics: list[fabric.Fabric],
) -> list[fabric.Fabric]:
    """Train model according to actual outcome.

    This must NOT be called for each adcall, but only for exploration ones.
    All fields of the fabrics need to be set.
    Returns the same data than the input.
    """
    return resources.get_instance().gb_model.report_buyers_status(fabrics)
