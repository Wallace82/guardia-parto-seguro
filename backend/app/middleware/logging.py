"""
GuardIA — Logging Middleware
"""
import time
import uuid
import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

log = structlog.get_logger(__name__)

class StructlogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            client_ip=request.client.host if request.client else None,
            method=request.method,
            path=request.url.path,
        )

        start_time = time.perf_counter()
        
        try:
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            
            # Não loga requisições de health check com INFO, mas debug
            log_level = log.debug if "/health" in request.url.path else log.info
            
            log_level(
                "request_completed",
                status_code=response.status_code,
                latency_ms=round(process_time * 1000, 2),
            )
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            process_time = time.perf_counter() - start_time
            log.exception(
                "request_failed",
                error=str(e),
                latency_ms=round(process_time * 1000, 2),
            )
            raise
