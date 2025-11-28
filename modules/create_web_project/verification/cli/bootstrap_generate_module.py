from __future__ import annotations

import argparse
from collections.abc import Iterable
from pathlib import Path

from ...phases.procedural.module_generator import ConfigError, generate_module_from_config, load_config


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a demo web module from deck config.")
    parser.add_argument("config", type=Path, help="Path to YAML/JSON deck config")
    parser.add_argument("--output-root", type=Path, default=None, help="Override output directory (defaults to demo_webs/projects)")
    parser.add_argument("--force", action="true", dest="force", default=False, help="Overwrite existing module directory")
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        # Load once to validate early; generate_module_from_config loads again but ensures same schema
        load_config(args.config)
        target = generate_module_from_config(args.config, output_root=args.output_root, force=args.force)
    except ConfigError as exc:
        print(f"[ERROR] {exc}")
        return 1
    print(f"[OK] Generated module at {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
