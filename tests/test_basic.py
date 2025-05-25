import os
import pathlib

from reef_cli.main import reef


def test_basic_python_file() -> None:
    file = f"{os.path.dirname(os.path.abspath(__file__))}/input/basic.py"

    reef(file_path=pathlib.Path(file))
