import time
from typing import Callable

from fastapi import FastAPI, Request, Response

from app.api.routes import api_router
from app.core.config import settings
from app.core.logging import configure_logging, logger


configure_logging()

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.middleware("http")
async def request_logging_middleware(
    request: Request, call_next: Callable[[Request], Response]
) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s - %s (%.2fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(api_router, prefix=settings.api_v1_prefix)

