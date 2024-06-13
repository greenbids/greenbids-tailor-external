from fastapi import FastAPI

from greenbids.tailor import fabric

from importlib.metadata import distribution

pkg_dist = distribution("greenbids-tailor")
app = FastAPI(
    title=" ".join(pkg_dist.name.split("-")).title(),
    summary=str(pkg_dist.metadata.json.get("summary")),
    description=str(pkg_dist.metadata.json.get("description")),
    version=pkg_dist.version,
)


@app.put("/")
async def get_buyers_probabilities(
    fabrics: list[fabric.Fabric],
) -> list[fabric.Fabric]:
    return fabrics


@app.post("/")
async def report_buyers_status(fabrics: list[fabric.Fabric]) -> list[fabric.Fabric]:
    return fabrics


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
