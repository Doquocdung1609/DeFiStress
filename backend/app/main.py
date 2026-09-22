from __future__ import annotations

import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import router
from backend.app.config import get_settings
from backend.app.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("defi_stress.api")

app = FastAPI(
    title="DeFiStress Lab API",
    version="0.1.0",
    description="Research Simulation — Mainnet Read-Only",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3100",
        "http://127.0.0.1:3100",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    started = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request complete",
        extra={"request_id": request_id, "duration_ms": round((perf_counter() - started) * 1000, 3)},
    )
    return response


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "DeFiStress Lab", "docs": "/docs", "safety": "Research Simulation — Mainnet Read-Only"}


app.include_router(router)
