from fastapi import (
    Request,
    HTTPException,
    status,
    responses,
    exceptions,
    exception_handlers,
)
from greenbids.tailor.core import fabric, models
from greenbids.tailor.core.app import resources
import typing

import logging

_logger = logging.getLogger(__name__)


async def model_not_ready_handler(request: Request, exc: resources.ModelNotReady):
    if not (request.method == "GET" and "healthz" in request.url.path):
        _logger.warning(
            "An access to the prediction model has been made, while it is not ready yet."
        )
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Model is not ready yet. Check readiness on route /healthz/readiness. Retry in few seconds.",
        headers={"gb-tailor-model-name": exc.model_name, "Retry-After": str(15)},
    )


async def unexpected_report_handler(request: Request, exc: models.UnexpectedReport):
    import pydantic

    del request

    ta = pydantic.TypeAdapter(list[fabric.Fabric])
    _logger.debug(
        "Report unexpected for the following request:\n"
        + str(ta.dump_python(exc.fabrics, exclude_defaults=True)),
        exc_info=exc,
    )
    return responses.JSONResponse(
        ta.dump_python(exc.fabrics, mode="json"),
        status_code=status.HTTP_202_ACCEPTED,
    )


async def request_validation_exception_handler(
    request: Request, exc: exceptions.RequestValidationError
):
    _logger.warning(
        "Unable to process the following request: \n%s\n%s", await request.body(), exc
    )
    return await exception_handlers.request_validation_exception_handler(request, exc)


EXCEPTION_HANDLERS: dict[
    typing.Union[int, type[Exception]],
    typing.Callable[[Request, typing.Any], typing.Coroutine],
] = {
    resources.ModelNotReady: model_not_ready_handler,
    models.UnexpectedReport: unexpected_report_handler,
    exceptions.RequestValidationError: request_validation_exception_handler,
}
