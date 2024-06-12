from greenbids.tailor._version import version
from fastapi import FastAPI

from greenbids.tailor import bid_request

app = FastAPI(
    title="Greenbids Tailor", summary="Traffic shaping for SSPs", version=version
)


@app.put("/")
async def get_buyers_probabilities(
    requests: list[bid_request.BidRequest],
) -> list[bid_request.BidRequest]:
    return requests


@app.post("/")
async def report_buyers_status(
    requests: list[bid_request.BidRequest], responses: list[bid_request.BidResponse]
) -> list[bid_request.BidRequest]:
    return requests


@app.get("/healthz/startup")
async def startup_probe():
    return {}


@app.get("/healthz/liveness")
async def liveness_probe():
    return {}


@app.get("/healthz/readiness")
async def readiness_probe():
    return {}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
