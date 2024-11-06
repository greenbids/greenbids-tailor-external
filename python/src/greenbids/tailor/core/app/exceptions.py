from fastapi import Request, HTTPException, status
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


EXCEPTION_HANDLERS: dict[
    typing.Union[int, type[Exception]],
    typing.Callable[[Request, typing.Any], typing.Coroutine],
] = {
    resources.ModelNotReady: model_not_ready_handler,
}
