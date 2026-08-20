from fastapi import FastAPI

from backend.app.api.routes.monitors import router as monitors_router

app = FastAPI(
    title="PulseWatch API",
    version="0.1.0",
)

app.include_router(monitors_router)


@app.get("/health")
def health():
    return {"status": "ok"}
