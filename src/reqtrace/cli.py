"""
cli.py
------
Entry point untuk perintah `reqtrace` di terminal.

Usage:
    reqtrace view logs/trace.json
    reqtrace view logs/trace.json --port 8080
    reqtrace view logs/trace.json --no-browser
"""

import argparse
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="reqtrace",
        description="reqtrace-py — HTTP request/response logger tools",
    )
    subparsers = parser.add_subparsers(dest="command")

    # --- subcommand: view ---
    view_parser = subparsers.add_parser(
        "view",
        help="Open Web UI log viewer for a JSON log file",
    )
    view_parser.add_argument(
        "file",
        help="Path to the JSON log file (e.g. logs/trace.json)",
    )
    view_parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port to run the viewer on (default: 8765)",
    )
    view_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically",
    )

    args = parser.parse_args()

    if args.command == "view":
        _cmd_view(args)
    else:
        parser.print_help()


def _cmd_view(args) -> None:
    from .viewer.server import start_viewer

    file_path = args.file

    if not os.path.exists(file_path):
        print(f"[reqtrace] Error: file not found: '{file_path}'")
        print(
            f"[reqtrace] Make sure reqtrace is configured with output='file' or output='both'"
        )
        sys.exit(1)

    if not file_path.endswith(".json"):
        print(f"[reqtrace] Error: only JSON log files are supported.")
        print(f"[reqtrace] Make sure file_format='json' in your ReqTrace config.")
        sys.exit(1)

    start_viewer(
        file_path=file_path,
        port=args.port,
        open_browser=not args.no_browser,
    )


if __name__ == "__main__":
    main()
