from fastapi import APIRouter
from greenbids.tailor.core import models
from greenbids.tailor.core.app.resources import APP_RESOURCES

router = APIRouter(tags=["Main"])


@router.put("/")
async def get_buyers_probabilities(
    fabrics: list[models.Model.GetBuyersProbabilitiesInput],
) -> list[models.Model.GetBuyersProbabilitiesOutput]:
    """Compute the probability of the buyers to provide a bid.

    This must be called for each adcall.
    """
    return APP_RESOURCES.gb_model.get_buyers_probabilities(fabrics)


@router.post("/")
async def report_buyers_status(
    fabrics: list[models.Model.ReportBuyersStatusInput],
) -> list[models.Model.ReportBuyersStatusOutput]:
    """Train model according to actual outcome.

    This must NOT be called for each adcall, but only for exploration ones.
    """
    return APP_RESOURCES.gb_model.report_buyers_status(fabrics)
