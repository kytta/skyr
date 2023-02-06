from typing import List

import pytest

import skyr


def test_main_returns_zero():
    assert skyr.main() == 0


@pytest.mark.parametrize(
    ("argv", "return_code"), [
        (["--help"], 0),
        (["--version"], 0),
    ],
)
def test_argpase_exits_zero(argv: List[str], return_code: int):
    with pytest.raises(SystemExit):
        assert skyr.main(argv) == return_code
