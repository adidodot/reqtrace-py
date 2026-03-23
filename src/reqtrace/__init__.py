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
from .differ import DiffResult, SnapshotStore, compute_diff
from .middleware import ReqTraceMiddleware

__all__ = [
    "ReqTrace",
    "ReqTraceMiddleware",
    "ReqTraceConfig",
    "DiffResult",
    "SnapshotStore",
    "compute_diff",
]

__version__ = "0.2.0"


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
    diff : bool
        Auto-diff mode. Compares each response against the previous
        response for the same endpoint automatically.
        Defaults to False.
    clear_key : str, optional
        Keyboard shortcut to clear the terminal. Defaults to "c".
        Set to None to disable.

    Examples
    --------
    # Terminal only
    rt = ReqTrace(output="terminal")

    # Dengan auto-diff
    rt = ReqTrace(output="terminal", diff=True)

    # Diff + simpan ke file
    rt = ReqTrace(output="both", file_path="logs/trace.json", diff=True)

    # Nonaktifkan clear key
    rt = ReqTrace(output="terminal", clear_key=None)

    # Disabled (e.g. in production)
    rt = ReqTrace(output="terminal", enabled=False)
    """

    def __init__(
        self,
        output: OutputMode = "terminal",
        file_path: str | None = None,
        file_format: FileFormat = "json",
        enabled: bool = True,
        diff: bool = False,
        clear_key: str | None = "c",
    ) -> None:
        self.config = ReqTraceConfig(
            output=output,
            file_path=file_path,
            file_format=file_format,
            enabled=enabled,
            diff=diff,
            clear_key=clear_key,
        )
