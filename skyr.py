#!/usr/bin/env python3
import argparse
import errno
import os
import sys
from pathlib import Path
from typing import Dict
from typing import Iterable
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Sequence
from typing import Union

__version__ = "0.2.0"


class SkyrError(Exception):
    def __init__(self, script_file: Path, error_message: str) -> None:
        self.file = script_file
        self.message = error_message

    def __str__(self) -> str:
        return f"{self.message}: {self.file}"


class ScriptNotFoundError(SkyrError):
    def __init__(self, script_file: Path) -> None:
        super().__init__(script_file, "script not found")


class ScriptIsNotAFileError(SkyrError):
    def __init__(self, script_file: Path) -> None:
        super().__init__(script_file, "script is not a file")


class ScriptIsNotExecutableError(SkyrError):
    def __init__(self, script_file: Path) -> None:
        super().__init__(script_file, "script is not executable")


def _print_scripts(scripts: Iterable[Path], header: str) -> None:
    indent = ""
    if sys.stdout.isatty():
        indent = "    "

        if sys.stderr.isatty():
            sys.stderr.write(f"{header}:\n")
            sys.stderr.flush()

    for script_file in scripts:
        script_name = script_file.name
        try:
            validate_script(script_file)
            sys.stdout.write(f"{indent}{script_name}")
        except SkyrError as exc:
            # TODO: check color support
            sys.stdout.write(
                f"{indent}\033[2;9m{script_name}\033[0m\t{exc.message}",
            )
        finally:
            sys.stdout.write("\n")

    sys.stdout.flush()


def _warn(msg: str) -> None:
    sys.stderr.write(f"[WARNING] {msg}\n")
    sys.stderr.flush()


def _err(msg: str) -> None:
    sys.stderr.write(f"[ERROR] {msg}\n")
    sys.stderr.flush()


def validate_script(script_file: Path) -> Path:
    """Validates the script file path.

    Checks if the path to the script file exists, is a file, and can be
    executed. If any of the checks doesn't pass, raises an exception.
    If the script seems to be valid, returns it's resolved path.

    :param script_file: Path to the script to validate
    :return: the validated and resolved path
    """
    if not script_file.exists():
        raise ScriptNotFoundError(script_file)

    if not script_file.is_file():
        raise ScriptIsNotAFileError(script_file)

    if not os.access(script_file, os.X_OK):
        raise ScriptIsNotExecutableError(script_file)

    return script_file.resolve()


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


def get_script_map(script_dir: Path) -> Dict[str, Path]:
    """Return a mapping of script names to the actual script files.

    Note that this method *does not* validate the scripts, but rather
    just returns the list of files in the directory.
    """
    return {
        path.name: path.resolve()
        for path in script_dir.iterdir()
        if path.is_file()
    }


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
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        default=argparse.SUPPRESS,
        help="show all available scripts and exit",
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

    script_map = get_script_map(script_dir)

    if hasattr(args, "list") and args.list:
        _print_scripts(script_map.values(), "Available scripts")
        raise SystemExit(0)

    if args.script not in script_map:
        _err(f"Can't find script: {args.script}")
        raise SystemExit(1)

    try:
        script_file = validate_script(script_map[args.script])
    except SkyrError as exc:
        _err(str(exc))
        raise SystemExit(1) from exc

    try_execute(args.script, script_file, rest)


if __name__ == "__main__":
    main()
