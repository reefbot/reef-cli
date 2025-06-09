import pathlib

from dataclasses import dataclass


@dataclass
class ImportNode:
    name: str
    origin: str
    file_path: pathlib.Path
    qualified_name: str
    alias: str = ""


@dataclass
class FuncNode:
    name: str
    params: str
    body: str
    code: str
    line_number_start: int
    line_number_end: int
    qualified_name: (
        str  # (where in the project it exists) i.e. src.module.module.definition + name
    )
    file_path: pathlib.Path  # directory of definition
    # parents: list["Node"]
    # children: list["Node"]


@dataclass
class ClassNode:
    name: str
    body: str
    code: str
    line_number_start: int
    line_number_end: int
    qualified_name: (
        str  # (where in the project it exists) i.e. src.module.module.definition + name
    )
    file_path: pathlib.Path  # directory of definition

    # parents: list["Node"]
    # children: list["Node"]