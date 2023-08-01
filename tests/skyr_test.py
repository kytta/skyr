import subprocess
import sys
from collections.abc import Iterable
from collections.abc import Sequence
from pathlib import Path
from typing import Optional

import pytest

import skyr

ASSETS_DIR = Path(__file__).parent / "assets"


@pytest.mark.parametrize(
    ("argv", "return_code"), [
        (["--help"], 0),
        (["--version"], 0),
    ],
)
def test_argpase_exits_zero(argv: list[str], return_code: int):
    with pytest.raises(SystemExit):
        assert skyr.main(argv) == return_code


@pytest.mark.parametrize(
    ("candidates", "return_value"), [
        ([], None),
        (["nonexistentdir"], None),
        (["script"], ASSETS_DIR / "script"),
        (["nonexistentdir", "other_dir"], ASSETS_DIR / "other_dir"),
        (["a_file"], None),
    ],
)
def test_find_dir(
    candidates: Iterable[str],
    return_value: Optional[Path],
    monkeypatch,
):
    with monkeypatch.context() as m:
        m.chdir(Path(__file__).parent / "assets")
        assert skyr.find_dir(candidates) == return_value


@pytest.mark.parametrize(
    ("name", "return_value", "expected_err"), [
        ("build", ASSETS_DIR / "script/build", None),
        ("doesnt-exist", None, "Script doesn't exist"),
        ("a_dir", None, "Script is not a file"),
    ],
)
def test_find_script(
    name: str,
    return_value: Optional[Path],
    expected_err: Optional[str],
    capsys,
):
    assert skyr.find_script(name, ASSETS_DIR / "script") == return_value

    if expected_err is not None:
        captured = capsys.readouterr()
        assert expected_err in captured.err


@pytest.mark.parametrize(
    ("name", "script_file", "expected_err"), [
        (
            "script/no-shebang",
            (ASSETS_DIR / "script/no-shebang").resolve(),
            "has a wrong executable format",
        ),
        (
            "script/not-executable",
            (ASSETS_DIR / "script/not-executable").resolve(),
            "You are not allowed to execute",
        ),
    ],
)
def test_try_execute(
    name: str,
    script_file: Path,
    expected_err: str,
    monkeypatch,
    capsys,
):
    with monkeypatch.context() as m:
        m.chdir(Path(__file__).parent / "assets")

        with pytest.raises(SystemExit) as excinfo:
            skyr.try_execute(name, script_file)

        assert excinfo.value.code == 1

        _, err = capsys.readouterr()
        assert expected_err in err


def test_main_warns_if_provided_script_dir_doesnt_exist(monkeypatch, capsys):
    with monkeypatch.context() as m:
        m.chdir(ASSETS_DIR / "bad_cwd")

        with pytest.raises(SystemExit):
            skyr.main(["--script-dir", "my-scripts"])

        _, err = capsys.readouterr()
        assert "Script directory not found" in err


@pytest.mark.parametrize(
    "argv", [
        ["doesnt_exist"],
        ["no-shebang"],
    ],
)
def test_main_fails(argv: Sequence[str], monkeypatch):
    with monkeypatch.context() as m:
        m.chdir(Path(__file__).parent / "assets")

        with pytest.raises(SystemExit) as excinfo:
            skyr.main(argv)

        assert excinfo.value.code == 1


def test_main_fails_if_no_script_dir_found(monkeypatch, capsys):
    with monkeypatch.context() as m:
        m.chdir(ASSETS_DIR / "bad_cwd")

        with pytest.raises(SystemExit) as excinfo:
            skyr.main()

        assert excinfo.value.code == 1

        _, err = capsys.readouterr()
        assert "No script directory found." in err


@pytest.mark.parametrize(
    ("argv", "expected_out"), [
        ([], b"I'm a build script"),
        (["hello"], b"Hello World!"),
        (
            ["--script-dir", "other_dir"],
            b"I'm a build script in a different directory",
        ),
    ],
)
def test_successful_execution(
    argv: list[str],
    expected_out: bytes,
    monkeypatch,
):
    with monkeypatch.context() as m:
        m.chdir(Path(__file__).parent / "assets")

        stdout = subprocess.check_output(
            [sys.executable, "-m", "skyr", *argv],  # noqa: S603
        )

        assert expected_out in stdout
