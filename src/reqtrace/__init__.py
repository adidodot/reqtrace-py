"""
reqtrace
--------
Lightweight HTTP request/response logger for FastAPI.

Quickstart
----------
from fastapi import FastAPI
from reqtrace import ReqTrace
from reqtrace.middleware import ReqTraceMiddleware

rt = ReqTrace(output="terminal")

app = FastAPI()
app.add_middleware(ReqTraceMiddleware, config=rt.config)
"""

from .config import ReqTraceConfig, OutputMode, FileFormat
from .middleware import ReqTraceMiddleware

__all__ = [
    "ReqTrace",
    "ReqTraceMiddleware",
    "ReqTraceConfig",
]

__version__ = "0.1.0"


class ReqTrace:
    """
    Main entry point for reqtrace configuration.

    Parameters
    ----------
    output : "terminal" | "file" | "both"
        Where to send log output.
    file_path : str, optional
        Required when output is "file" or "both".
    file_format : "json" | "txt"
        Log file format. Defaults to "json".
    enabled : bool
        Master on/off switch. Defaults to True.

    Examples
    --------
    # Terminal only
    rt = ReqTrace(output="terminal")

    # File only (JSON)
    rt = ReqTrace(output="file", file_path="logs/trace.json")

    # Both outputs, txt format
    rt = ReqTrace(output="both", file_path="logs/trace.txt", file_format="txt")

    # Disabled (e.g. in production)
    rt = ReqTrace(output="terminal", enabled=False)
    """

    def __init__(
        self,
        output: OutputMode = "terminal",
        file_path: str | None = None,
        file_format: FileFormat = "json",
        enabled: bool = True,
    ) -> None:
        self.config = ReqTraceConfig(
            output=output,
            file_path=file_path,
            file_format=file_format,
            enabled=enabled,
        )

    def middleware(self):
        """
        Return the middleware class pre-bound with this config.
        Convenience method for app.add_middleware().

        Usage
        -----
        app.add_middleware(rt.middleware(), ...)  # wrong
        app.add_middleware(ReqTraceMiddleware, config=rt.config)  # correct
        """
        return ReqTraceMiddleware
