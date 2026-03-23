# reqtrace

Lightweight HTTP request/response logger for FastAPI. Designed for developers who need clear, structured debug output without writing `print()` everywhere.

## Features

- Auto-log every request & response via FastAPI middleware
- Colorized terminal output with status color coding
- File output in JSON (NDJSON) or plain text format
- Configurable output mode: terminal, file, or both
- Authorization header auto-masking

## Installation

```bash
pip install reqtrace
```

## Quickstart

```python
from fastapi import FastAPI
from reqtrace import ReqTrace
from reqtrace.middleware import ReqTraceMiddleware

rt = ReqTrace(output="terminal")

app = FastAPI()
app.add_middleware(ReqTraceMiddleware, config=rt.config)
```

That's it — every request will be logged automatically.

## Output Modes

```python
# Terminal only (default)
rt = ReqTrace(output="terminal")

# File only — JSON format
rt = ReqTrace(output="file", file_path="logs/trace.json")

# File only — plain text
rt = ReqTrace(output="file", file_path="logs/trace.txt", file_format="txt")

# Both terminal and file
rt = ReqTrace(output="both", file_path="logs/trace.json")

# Disabled (useful for production)
rt = ReqTrace(output="terminal", enabled=False)
```

## Terminal Output Example

```
┌─ REQUEST ────────────────────────────────────────────────────
  POST    /api/users
  content-type: application/json
  Body:
    {
      "name": "Diz",
      "email": "diz@mail.com"
    }
├─ RESPONSE ───────────────────────────────────────────────────
  Status :  422  43.2ms
  Body:
    {
      "detail": [{"loc": ["body", "email"], "msg": "value is not a valid email"}]
    }
└──────────────────────────────────────────────────────────────
```

Status codes are color-coded:

- 🟢 `2xx` — green
- 🟡 `3xx` — yellow
- 🔴 `4xx` — red
- 🟣 `5xx` — magenta

## JSON Log Format

Each entry is one JSON object per line (NDJSON), easy to stream and parse:

```json
{"timestamp": "2026-03-23T10:15:00+00:00", "method": "POST", "url": "/api/users", "status_code": 422, "latency_ms": 43.2, "request_headers": {...}, "request_body": {"name": "Diz"}, "response_body": {...}}
```

## Requirements

- Python >= 3.10
- FastAPI / Starlette >= 0.27.0

## Roadmap

- `v0.2.0` — Response diffing (compare two responses, highlight field changes)
- `v0.2.0` — Flask/Django support
- `v0.3.0` — Filter by route, method, or status code
- `v0.3.0` — Web UI log viewer

## License

MIT
