import json
import os
from datetime import datetime, timezone
from typing import Any, Optional

from .config import FileFormat


def _build_record(
    method: str,
    url: str,
    status_code: int,
    latency_ms: float,
    request_headers: Optional[dict] = None,
    request_body: Any = None,
    response_body: Any = None,
) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "url": url,
        "status_code": status_code,
        "latency_ms": round(latency_ms, 2),
        "request_headers": request_headers or {},
        "request_body": request_body,
        "response_body": response_body,
    }


def _ensure_dir(file_path: str) -> None:
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def write_log(
    file_path: str,
    file_format: FileFormat,
    method: str,
    url: str,
    status_code: int,
    latency_ms: float,
    request_headers: Optional[dict] = None,
    request_body: Any = None,
    response_body: Any = None,
) -> None:
    """
    Append a log entry to the specified file.

    For JSON format  : appends a JSON object per line (newline-delimited JSON / NDJSON).
    For txt format   : appends a human-readable block of text.
    """
    _ensure_dir(file_path)
    record = _build_record(
        method,
        url,
        status_code,
        latency_ms,
        request_headers,
        request_body,
        response_body,
    )

    if file_format == "json":
        _write_json(file_path, record)
    else:
        _write_txt(file_path, record)


def _write_json(file_path: str, record: dict) -> None:
    """Append one JSON object per line (NDJSON format) — easy to parse & stream."""
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _write_txt(file_path: str, record: dict) -> None:
    """Append a human-readable text block."""
    sep = "-" * 60
    body_req = (
        json.dumps(record["request_body"], ensure_ascii=False)
        if record["request_body"]
        else "(empty)"
    )
    body_res = (
        json.dumps(record["response_body"], ensure_ascii=False)
        if record["response_body"]
        else "(empty)"
    )

    entry = (
        f"\n{sep}\n"
        f"[{record['timestamp']}]\n"
        f"  {record['method']} {record['url']}\n"
        f"  Status  : {record['status_code']}\n"
        f"  Latency : {record['latency_ms']}ms\n"
        f"  Req Body: {body_req}\n"
        f"  Res Body: {body_res}\n"
        f"{sep}\n"
    )

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(entry)
