from __future__ import annotations

import argparse
import importlib
import sys
from collections.abc import Callable, Sequence

CommandRunner = Callable[[Sequence[str]], int | None]


def _load_runner(module_path: str) -> CommandRunner:
    module = importlib.import_module(module_path, package=__package__)
    runner = getattr(module, "main", None)
    if not callable(runner):
        raise RuntimeError(f"Module '{module_path}' does not expose a main() function")
    return runner


COMMANDS: dict[str, tuple[str, str]] = {
    "verify": ("Run the full verification pipeline for one or more projects.", "modules.web_verification.phases.procedural.verify_project"),
    "run-deck": ("Execute procedural + visual checks for a deck file.", "modules.web_verification.phases.procedural.run_deck_pipeline"),
    "flow-screenshots": ("Capture the canned demo-web flows (autozone/autocrm).", "modules.web_verification.cli.visual.flow_screenshots"),
    "project-screenshots": ("Auto-discover a project's pages and capture screenshots.", "modules.web_verification.cli.visual.project_screenshots"),
    "analyze-sandbox": ("Summarize miner/agent datasets for unresolved or trivial tasks.", "modules.web_verification.cli.bootstrap_analyze_sandbox"),
    "generate-module": ("Bootstrap a demo_webs module from a YAML/JSON config.", "modules.web_verification.cli.bootstrap_generate_module"),
    "verify-template": ("Verify that the autodining template matches web_4_autodining.", "modules.web_verification.cli.bootstrap_verify_template"),
}


def main(argv: Sequence[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="python -m modules.web_verification",
        description="Web verification tooling (verification pipeline, screenshots, sandbox analysis, etc.).",
        add_help=True,
    )
    parser.add_argument("command", nargs="?", help=f"One of: {', '.join(COMMANDS)}")
    parser.add_argument("command_args", nargs=argparse.REMAINDER, help="Arguments forwarded to the selected command.")
    if not args:
        parser.print_help()
        return 0
    parsed = parser.parse_args(args[:1])
    command = parsed.command
    if command not in COMMANDS:
        print(f"❌ Unknown command '{command}'. Available: {', '.join(COMMANDS)}")
        return 2
    description, module_path = COMMANDS[command]
    runner = _load_runner(module_path)
    forwarded = args[1:]
    if forwarded and forwarded[0] == "--":
        forwarded = forwarded[1:]
    # Show contextual help
    if forwarded and forwarded[0] in {"-h", "--help"}:
        help_module = importlib.import_module(module_path, package=__package__)
        help_parser = getattr(help_module, "parse_args", None)
        if callable(help_parser):
            try:
                help_parser(["--help"])
            except SystemExit as exc:
                return exc.code or 0
            return 0
        print(description)
        print("This command does not expose a custom --help handler.")
        return 0
    try:
        exit_code = runner(forwarded)
    except SystemExit as exc:
        return exc.code or 0
    return exit_code if isinstance(exit_code, int) else 0


if __name__ == "__main__":
    raise SystemExit(main())
