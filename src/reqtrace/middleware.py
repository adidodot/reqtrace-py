import json
import time
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from .config import ReqTraceConfig
from .formatter import format_log
from .writer import write_log


class ReqTraceMiddleware(BaseHTTPMiddleware):
    """
    FastAPI / Starlette middleware that logs every incoming
    request and its response.

    Usage
    -----
    rt = ReqTrace(output="both", file_path="logs/trace.json")
    app.add_middleware(ReqTraceMiddleware, config=rt.config)
    """

    def __init__(self, app: ASGIApp, config: ReqTraceConfig) -> None:
        super().__init__(app)
        self.config = config

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[override]
        if not self.config.enabled:
            return await call_next(request)

        # --- capture request body ---
        request_body = await self._read_request_body(request)

        # --- call the actual route ---
        start = time.perf_counter()
        response = await call_next(request)
        latency_ms = (time.perf_counter() - start) * 1000

        # --- capture response body ---
        response_body, response = await self._read_response_body(response)

        # --- dispatch to configured outputs ---
        method: str = request.method
        url: str = str(request.url.path)
        status_code: int = response.status_code

        if self.config.use_terminal:
            print(
                format_log(
                    method=method,
                    url=url,
                    status_code=status_code,
                    latency_ms=latency_ms,
                    request_headers=dict(request.headers),
                    request_body=request_body,
                    response_body=response_body,
                )
            )

        if self.config.use_file and self.config.file_path is not None:
            write_log(
                file_path=self.config.file_path,
                file_format=self.config.file_format,
                method=method,
                url=url,
                status_code=status_code,
                latency_ms=latency_ms,
                request_headers=dict(request.headers),
                request_body=request_body,
                response_body=response_body,
            )

        return response

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    async def _read_request_body(self, request: Request) -> Any:
        """Read and parse request body without consuming the stream."""
        raw: bytes = b""
        try:
            raw = await request.body()
            if not raw:
                return None
            # re-inject body so the route handler can still read it
            request._body = raw  # type: ignore[attr-defined]
            return json.loads(raw)
        except Exception:
            return raw.decode("utf-8", errors="replace") if raw else None

    async def _read_response_body(self, response: Response) -> tuple[Any, Response]:
        """
        Read the response body stream, then rebuild a fresh Response
        so the client still receives the full body.
        """
        body_chunks: list[bytes] = []
        async for chunk in response.body_iterator:  # type: ignore[attr-defined]
            body_chunks.append(chunk if isinstance(chunk, bytes) else chunk.encode())

        raw = b"".join(body_chunks)

        parsed: Any = None
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = raw.decode("utf-8", errors="replace") if raw else None

        # rebuild a fresh response with the same status/headers/body
        new_response = Response(
            content=raw,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

        return parsed, new_response
