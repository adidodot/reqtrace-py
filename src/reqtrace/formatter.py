from typing import Any, Optional


# ANSI color codes
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # status colors
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"


def _colorize(text: str, *codes: str) -> str:
    return "".join(codes) + text + Color.RESET


def _status_color(status_code: int) -> str:
    if status_code < 300:
        return Color.GREEN
    elif status_code < 400:
        return Color.YELLOW
    elif status_code < 500:
        return Color.RED
    return Color.MAGENTA


def _format_body(body: Any, indent: int = 2) -> str:
    """Format request/response body for display."""
    if body is None:
        return _colorize("(empty)", Color.GRAY)

    if isinstance(body, (dict, list)):
        import json

        try:
            formatted = json.dumps(body, indent=indent, ensure_ascii=False)
            # limit long bodies
            lines = formatted.splitlines()
            if len(lines) > 20:
                truncated = "\n".join(lines[:20])
                return f"{truncated}\n  {_colorize(f'... ({len(lines) - 20} more lines)', Color.GRAY)}"
            return formatted
        except Exception:
            return str(body)

    text = str(body)
    if len(text) > 500:
        return text[:500] + _colorize(
            f" ... ({len(text) - 500} more chars)", Color.GRAY
        )
    return text


def format_log(
    method: str,
    url: str,
    status_code: int,
    latency_ms: float,
    request_headers: Optional[dict] = None,
    request_body: Any = None,
    response_body: Any = None,
) -> str:
    """
    Build a colorized, human-readable log string for terminal output.
    """
    status_col = _status_color(status_code)
    border = _colorize("─" * 52, Color.GRAY)

    method_str = _colorize(f"{method:<6}", Color.CYAN, Color.BOLD)
    url_str = _colorize(url, Color.WHITE, Color.BOLD)
    status_str = _colorize(str(status_code), status_col, Color.BOLD)
    latency_str = _colorize(f"{latency_ms:.1f}ms", Color.GRAY)

    lines = [
        "",
        _colorize("┌─ REQUEST ", Color.GRAY) + border,
        f"  {method_str}  {url_str}",
    ]

    # request headers (only show Content-Type & Authorization to keep it brief)
    if request_headers:
        shown = {
            k: v
            for k, v in request_headers.items()
            if k.lower() in ("content-type", "authorization", "accept")
        }
        if shown:
            for k, v in shown.items():
                val = v if k.lower() != "authorization" else v[:20] + "..."
                lines.append(
                    f"  {_colorize(k + ':', Color.GRAY)} {_colorize(val, Color.DIM)}"
                )

    # request body
    if request_body:
        lines.append(f"  {_colorize('Body:', Color.GRAY)}")
        for line in _format_body(request_body).splitlines():
            lines.append(f"    {line}")

    lines.append(_colorize("├─ RESPONSE ", Color.GRAY) + border)
    lines.append(f"  {_colorize('Status :', Color.GRAY)}  {status_str}  {latency_str}")

    # response body
    if response_body:
        lines.append(f"  {_colorize('Body:', Color.GRAY)}")
        for line in _format_body(response_body).splitlines():
            lines.append(f"    {line}")

    lines.append(_colorize("└" + "─" * 62, Color.GRAY))

    return "\n".join(lines)
