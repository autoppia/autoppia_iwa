from __future__ import annotations

from typing import Iterable

from ..verify_project import main as verify_main


def main(argv: Iterable[str] | None = None) -> int:
    return verify_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
