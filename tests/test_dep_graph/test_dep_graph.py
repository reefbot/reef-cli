import os
import pathlib

from reef_cli.extraction.utils import get_all_files_extension


def test_get_all_files_extension():
    project_dir = pathlib.Path(os.path.dirname(__file__), os.path.pardir, "dummy_proj")
    all_files = get_all_files_extension(project_dir, ext=".py")

    expected_all_python_files = [
        pathlib.PosixPath(
            "/Users/tomcarter/reef/reef-cli/tests/test_dep_graph/../dummy_proj/__init__.py"
        ),
        pathlib.PosixPath(
            "/Users/tomcarter/reef/reef-cli/tests/test_dep_graph/../dummy_proj/main.py"
        ),
        pathlib.PosixPath(
            "/Users/tomcarter/reef/reef-cli/tests/test_dep_graph/../dummy_proj/hello_world/hello_world.py"
        ),
        pathlib.PosixPath(
            "/Users/tomcarter/reef/reef-cli/tests/test_dep_graph/../dummy_proj/hello_world/__init__.py"
        ),
    ]

    assert all_files == expected_all_python_files
