#!/usr/bin/env python3
import argparse
from importlib import metadata
from pathlib import Path
from typing import Optional
from typing import Sequence

__version__ = metadata.version("skyr")


def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="A low-fat task runner, Skyr runs scripts from the "
                    "'./scripts/' directory in a make(1) fashion.",
        epilog="Source code: <https://github.com/kytta/skyr>",
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=__version__,
    )
    parser.add_argument(
        "script",
        nargs="?",
        default="build",
        type=str,
        help="The name of the script to run.",
        metavar="SCRIPT",
    )
    parser.add_argument(
        "--config-dir",
        default="./scripts/",
        type=Path,
        help="Location of the script files.",
        metavar="DIR",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _get_parser()
    args, rest = parser.parse_known_args(argv)
    return 0


if __name__ == "__main__":
    raise (SystemExit(main()))
