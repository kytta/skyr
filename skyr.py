#!/usr/bin/env python3
import argparse
import sys
from importlib import metadata
from pathlib import Path
from typing import Optional
from typing import Sequence

__version__ = metadata.version("skyr")

DEFAULT_DIR = Path("./scripts/")


def _err(msg: str) -> None:
    sys.stderr.write(f"[ERROR] {msg}\n")
    sys.stderr.flush()


def find_script(name: str, script_dir: Path = DEFAULT_DIR) -> Optional[Path]:
    """Tries to find a script to run."""
    resolved_script_dir = script_dir.resolve()

    if not resolved_script_dir.exists():
        _err(f"Directory {script_dir!r} doesn't exist.")
        return None

    if not resolved_script_dir.is_dir():
        _err(f"{script_dir!r} is not a directory.")
        return None

    script_file = resolved_script_dir / name

    if not script_file.exists():
        _err(f"Script {name!r} doesn't exist in {script_dir}.")
        return None

    if not script_file.is_file():
        _err(f"{script_file!r} is not a file.")
        return None

    return script_file


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
        "--script-dir",
        default=DEFAULT_DIR,
        type=Path,
        help="Location of the script files.",
        metavar="DIR",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args, rest = _get_parser().parse_known_args(argv)

    script_file = find_script(args.script, script_dir=args.script_dir)

    if script_file is None:
        _err(f"Couldn't find script {args.script!r}")
        return 1

    return 0


if __name__ == "__main__":
    raise (SystemExit(main()))
