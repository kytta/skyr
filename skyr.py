#!/usr/bin/env python3
import argparse
import errno
import os
import sys
from importlib import metadata
from pathlib import Path
from typing import Iterable
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import Union

__version__ = metadata.version("skyr")


def _warn(msg: str) -> None:
    sys.stderr.write(f"[WARNING] {msg}\n")
    sys.stderr.flush()


def _err(msg: str) -> None:
    sys.stderr.write(f"[ERROR] {msg}\n")
    sys.stderr.flush()


def find_dir(candidates: Iterable[Union[str, Path]]) -> Optional[Path]:
    """Searches an array for an existent directory.

    :param candidates: Directories or names that will be searched
    :return: First existent directory, or ``None`` if not found.
    """
    for candidate in candidates:
        candidate_path = Path(candidate)
        if candidate_path.is_dir() and candidate_path.exists():
            return candidate_path.resolve()

    return None


def find_script(name: str, script_dir: Path) -> Optional[Path]:
    """Tries to find a script to run.

    :param name: Name of the script
    :param script_dir: Directory to search for the scripts
    """
    script_file = (script_dir / name).resolve()

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
        default=argparse.SUPPRESS,
        type=Path,
        help="Script directory. If not provided, Skyr will look for scripts in"
             "'.skyr' and then 'script'",
        metavar="DIR",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> NoReturn:
    args, rest = _get_parser().parse_known_args(argv)

    script_dir = None
    if hasattr(args, "script_dir"):
        if args.script_dir.exists():
            script_dir = args.script_dir
        else:
            _warn(f"Script directory not found: {str(args.script_dir)}")

    if script_dir is None:
        script_dir = find_dir([Path(".skyr"), Path("script")])

    if script_dir is None:
        _err("No script directory found.")
        raise SystemExit(1)

    script_file = find_script(args.script, script_dir=script_dir)
    if script_file is None:
        _err(f"Couldn't find script {args.script!r}")
        raise SystemExit(1)

    try_execute(f"{script_dir / args.script}", script_file, rest)


if __name__ == "__main__":
    main()
