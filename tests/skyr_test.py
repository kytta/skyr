import subprocess
from contextlib import nullcontext
from pathlib import Path
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence

import pytest

import skyr

ASSETS_DIR = Path(__file__).parent / "assets"


@pytest.mark.parametrize(
    ("argv", "return_code"), [
        (["--help"], 0),
        (["--version"], 0),
    ],
)
def test_argpase_exits_zero(argv: List[str], return_code: int):
    with pytest.raises(SystemExit):
        assert skyr.main(argv) == return_code


@pytest.mark.parametrize(
    ("input_path", "context", "expected"), [
        (
            ASSETS_DIR / "script/build",
            nullcontext(),
            (ASSETS_DIR / "script/build").resolve(),
        ),
        (
            ASSETS_DIR / "idonotexist",
            pytest.raises(skyr.ScriptNotFoundError),
            None,
        ),
        (
            ASSETS_DIR / "script/a_dir",
            pytest.raises(skyr.ScriptIsNotAFileError),
            None,
        ),
        (
            ASSETS_DIR / "script/not-executable",
            pytest.raises(skyr.ScriptIsNotExecutableError),
            None,
        ),
    ],
)
def test_validate_script(input_path: Path, context, expected):
    with context:
        retval = skyr.validate_script(input_path)

    if expected is not None:
        assert retval == expected


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


def test_get_script_map():
    retval = skyr.get_script_map(ASSETS_DIR / "script")

    # Test that a normal script resolves
    assert "build" in retval
    assert retval["build"] == (ASSETS_DIR / "script/build").resolve()

    # Test inclusion of other script files
    assert "hello" in retval
    assert "no-shebang" in retval
    assert "not-executable" in retval

    # Test that only files are in the list
    assert "a_dir" not in retval


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
    argv: List[str],
    expected_out: bytes,
    monkeypatch,
):
    with monkeypatch.context() as m:
        m.chdir(Path(__file__).parent / "assets")

        cmd = ["python3", "-m", "skyr", *argv]
        result = subprocess.run(cmd, capture_output=True)

        assert result.returncode == 0
        assert expected_out in result.stdout


def test_list(capsys, monkeypatch):
    with monkeypatch.context() as m:
        m.chdir(ASSETS_DIR)

        with pytest.raises(SystemExit) as excinfo:
            skyr.main(["--list"])

        assert excinfo.value.code == 0

        # Check that the scripts are listed
        # Keep in mind that the scripts are not validated at this point
        out, err = capsys.readouterr()
        assert "build" in out
        assert "hello" in out
        assert "no-shebang" in out
        assert "not-executable" in out

        # By default, the captured stdout/stderr are not TTY
        assert "Available scripts" not in err


@pytest.mark.parametrize(
    "is_stderr_a_tty", [
        False,
        True,
    ],
)
def test_list_in_a_tty(is_stderr_a_tty: bool, capsys, monkeypatch):
    with monkeypatch.context() as m:
        m.chdir(ASSETS_DIR)
        m.setattr("sys.stdout.isatty", lambda: True)
        m.setattr("sys.stderr.isatty", lambda: is_stderr_a_tty)

        with pytest.raises(SystemExit):
            skyr.main(["--list"])

        _, err = capsys.readouterr()
        if is_stderr_a_tty:
            assert "Available scripts" in err
        else:
            assert "Available scripts" not in err
