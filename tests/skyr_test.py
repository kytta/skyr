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
    ("name", "script_dir", "return_value", "expected_output"), [
        ("build", None, ASSETS_DIR / "scripts/build", None),
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
    expected_output: Optional[str],
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

        if expected_output is not None:
            assert expected_output in captured.err


@pytest.mark.parametrize(
    ("argv", "return_code", "expected_out", "expected_err"), [
        ([], 0, b"I'm a build script", None),
        (["hello"], 0, b"Hello World!", None),
        (
            ["--script-dir", "other_dir"], 0,
            b"I'm a build script in a different directory", None,
        ),
        (["no-shebang"], 1, None, b"has a wrong executable format"),
        (["not-executable"], 1, None, b"You are not allowed to execute"),
    ],
)
def test_execution(
    argv: List[str],
    return_code: int,
    expected_out: Optional[bytes],
    expected_err: Optional[bytes],
    monkeypatch,
):
    with monkeypatch.context() as m:
        m.chdir(Path(__file__).parent / "assets")

        cmd = ["python3", "-m", "skyr", *argv]
        result = subprocess.run(cmd, capture_output=True)

        assert result.returncode == return_code

        if expected_out is not None:
            assert expected_out in result.stdout

        if expected_err is not None:
            assert expected_err in result.stderr
