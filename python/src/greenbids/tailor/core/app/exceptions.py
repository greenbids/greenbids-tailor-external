from fastapi import Request, HTTPException, status
from greenbids.tailor.core.app import resources
import typing


async def model_not_ready_handler(request: Request, exc: resources.ModelNotReady):
    del request
    raise HTTPException(
        status_code=status.HTTP_425_TOO_EARLY,
        detail="Model is not ready yet. Check readiness on route /healthz/readiness. Retry in few seconds.",
        headers={"gb-tailor-model-name": exc.model_name},
    )


EXCEPTION_HANDLERS: dict[
    typing.Union[int, type[Exception]],
    typing.Callable[[Request, typing.Any], typing.Coroutine],
] = {
    resources.ModelNotReady: model_not_ready_handler,
}
