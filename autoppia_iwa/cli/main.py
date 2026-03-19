"""iwa CLI router."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable


COMMAND_HELP = {
    "check": "Health-check demo websites",
    "benchmark": "Run benchmark against a web agent",
    "generate-tasks": "Generate tasks to JSON",
    "verify": "Run web verification pipeline",
    "debug": "Launch debugger UI for trace inspection",
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="iwa", description="CLI for Autoppia IWA")
    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments forwarded to the command")
    return parser


def _resolve_command(command: str) -> Callable[[], None]:
    if command == "check":
        from autoppia_iwa.entrypoints.check.run import main as cmd
    elif command == "benchmark":
        from autoppia_iwa.entrypoints.benchmark.run import main as cmd
    elif command == "generate-tasks":
        from autoppia_iwa.entrypoints.generate_tasks.run import main as cmd
    elif command == "verify":
        from autoppia_iwa.entrypoints.web_verification.run import main as cmd
    elif command == "debug":
        from modules.debugger.server import main as cmd
    else:
        raise KeyError(command)
    return cmd


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if not args.command:
        _print_help()
        return 0

    try:
        cmd = _resolve_command(args.command)
    except KeyError:
        print(f"Unknown command: {args.command}")
        _print_help()
        return 1

    sys.argv = [f"iwa {args.command}"] + list(args.args)
    cmd()
    return 0


def _print_help() -> None:
    print("usage: iwa <command> [options]\n")
    print("commands:")
    for name, description in COMMAND_HELP.items():
        print(f"  {name:<14} {description}")
    print("\nRun 'iwa <command> --help' for details on each command.")


if __name__ == "__main__":
    raise SystemExit(main())
