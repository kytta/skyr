#!/usr/bin/env python3
import argparse
import errno
import os
import sys
from importlib import metadata
from pathlib import Path
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Sequence

__version__ = metadata.version("skyr")

DEFAULT_DIR = Path("./script/")


def _err(msg: str) -> None:
    sys.stderr.write(f"[ERROR] {msg}\n")
    sys.stderr.flush()


def find_script(name: str, script_dir: Path = DEFAULT_DIR) -> Optional[Path]:
    """Tries to find a script to run."""
    resolved_script_dir = script_dir.resolve()

    if not resolved_script_dir.exists():
        _err(f"Script directory doesn't exist: {str(resolved_script_dir)}")
        return None

    if not resolved_script_dir.is_dir():
        _err(f"Script directory is not a directory: {str(script_dir)}")
        return None

    script_file = resolved_script_dir / name

    if not script_file.exists():
        _err(f"Script doesn't exist: {str(script_file)}")
        return None

    if not script_file.is_file():
        _err(f"Script is not a file: {str(script_file)}")
        return None

    return script_file


def try_execute(
    name: str,
    script_file: Path,
    argv: Optional[List[str]] = None,
) -> NoReturn:
    if argv is None:
        argv = []

    try:
        os.execl(script_file, name, *argv)
    except OSError as exc:
        if exc.errno is errno.EACCES:
            _err(
                f"You are not allowed to execute {str(script_file)}. Please "
                "make sure that you've set the correct rights via chmod.", )
        elif exc.errno is errno.ENOEXEC:
            _err(
                f"{str(script_file)} has a wrong executable format. Did you "
                "forget to add a shebang?",
            )
        else:
            _err(f"Could not execute {str(script_file)}: {exc.strerror}")
        raise SystemExit(1) from exc


def _get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="A low-fat task runner, Skyr runs scripts from the "
                    "'./script/' directory in a make(1) fashion.",
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


def main(argv: Optional[Sequence[str]] = None) -> NoReturn:
    args, rest = _get_parser().parse_known_args(argv)

    script_file = find_script(args.script, script_dir=args.script_dir)

    if script_file is None:
        _err(f"Couldn't find script {args.script!r}")
        raise SystemExit(1)

    try_execute(f"{args.script_dir / args.script}", script_file, rest)


if __name__ == "__main__":
    main()
