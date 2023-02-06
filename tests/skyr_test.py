import subprocess
from pathlib import Path
from typing import List
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
def test_argpase_exits_zero(argv: List[str], return_code: int):
    with pytest.raises(SystemExit):
        assert skyr.main(argv) == return_code


@pytest.mark.parametrize(
    ("name", "script_dir", "return_value", "expected_err"), [
        ("build", None, ASSETS_DIR / "script/build", None),
        ("build", "./other_dir", ASSETS_DIR / "other_dir/build", None),
        ("build", "./doesnt-exist", None, "Script directory doesn't exist"),
        ("build", "./a_file", None, "Script directory is not a directory"),
        ("doesnt-exist", None, None, "Script doesn't exist"),
        ("a_dir", None, None, "Script is not a file"),
    ],
)
def test_find_script(
    name: str,
    script_dir: Optional[str],
    return_value: Optional[Path],
    expected_err: Optional[str],
    capsys,
    monkeypatch,
):
    with monkeypatch.context() as m:
        m.chdir(Path(__file__).parent / "assets")

        if script_dir is None:
            actual = skyr.find_script(name)
        else:
            actual = skyr.find_script(name, Path(script_dir))
        captured = capsys.readouterr()

        assert actual == return_value

        if expected_err is not None:
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


@pytest.mark.parametrize(
    "script_name", [
        "doesnt_exist",
        "no-shebang",
    ],
)
def test_main(script_name: str, monkeypatch):
    with monkeypatch.context() as m:
        m.chdir(Path(__file__).parent / "assets")

        with pytest.raises(SystemExit) as excinfo:
            skyr.main(script_name)

        assert excinfo.value.code == 1


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
