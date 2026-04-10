"""iwa CLI router."""

from __future__ import annotations

import sys
from collections.abc import Callable

COMMAND_HELP = {
    "check": "Health-check demo websites",
    "benchmark": "Run benchmark against a web agent",
    "generate-tasks": "Generate tasks to JSON",
    "verify": "Run web verification pipeline",
    "debug": "Launch debugger UI for trace inspection",
}


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
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {"-h", "--help"}:
        _print_help()
        return 0

    command = argv[0]
    forwarded_args = list(argv[1:])

    if command == "help":
        if not forwarded_args:
            _print_help()
            return 0
        command = forwarded_args[0]
        forwarded_args = ["--help", *forwarded_args[1:]]

    try:
        cmd = _resolve_command(command)
    except KeyError:
        print(f"Unknown command: {command}")
        _print_help()
        return 1

    sys.argv = [f"iwa {command}", *forwarded_args]
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
